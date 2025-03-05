from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import pandas as pd
from get_tutors import get_schedule
import os
import random
from main_auto_email import email_matched_student, email_matched_tutor, email_not_matched_student
from models import Student, Tutor
from scheduler import match_students_tutors

app = Flask(__name__, static_folder='static')
app.secret_key = '0599db35270c938d478af4964d9c00aa'

# Define upload folder path
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

is_uploaded = False
all_students = []

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    global is_uploaded, all_students
    message = None
    if request.method == 'POST':
        if 'peer_tutor_responses_file' in request.files and 'student_responses_file' in request.files:
            tutor_file = request.files['peer_tutor_responses_file']
            student_file = request.files['student_responses_file']

            if tutor_file.filename != '' and student_file.filename != '':
                try:
                    tutor_path = os.path.join(app.config['UPLOAD_FOLDER'], tutor_file.filename)
                    tutor_file.save(tutor_path)
                    
                    student_path = os.path.join(app.config['UPLOAD_FOLDER'], student_file.filename)
                    student_file.save(student_path)

                    df = pd.read_csv(student_path)
                    all_students = df["Student's Name (first and last)"].tolist()
                    
                    get_schedule(student_path, tutor_path, os.path.join(app.config['UPLOAD_FOLDER'], "saved_schedule.csv"))
                    message = f"Upload successful! Go to the <a class='text_link', href='{url_for('search')}'>Search</a> page to view or download assignments."
                    is_uploaded = True
                except Exception as e:
                    message = f"Error processing files: {str(e)}"
            else:
                message = "Please select both files"
        else:
            message = "Please upload both required files"

    return render_template('upload.html', message=message)

@app.route('/search', methods=['GET', 'POST'])
def search():
    global is_uploaded, all_students

    # Convert DataFrame rows to a list of dictionaries for the template
    assignments = []
    matched_students = []
    if is_uploaded:
        saved_schedule_path = os.path.join(app.config['UPLOAD_FOLDER'], "saved_schedule.csv")
        data = pd.read_csv(saved_schedule_path)
        # Get the column headers from the DataFrame
        for index, row in data.iterrows():
            subjects_tutor =  row['Tutor Courses'].split(", ")
            subjects_student = row['Student Courses'].split(", ")
            subjects_both = []
            for subject in subjects_tutor:
                if subject in subjects_student:
                    subjects_both.append(subject)
            matched_students.append(row['Student Name'])
            assignment = {
                'student': row['Student Name'] if 'Student Name' in row else row[0],  # Fallback to first column if header not found
                'tutor': row['Tutor Name'] if 'Tutor Name' in row else row[1],       # Fallback to second column if header not found
                'subject': ", ".join(subjects_both),
                'time_slot': row['Time'] if 'Time' in row else ''
            }
            assignments.append(assignment)
    
    # Sort the assignments list by tutor name first, then student name
    assignments.sort(key=lambda x: (x['tutor'].lower(), x['student'].lower()))

    unassigned_students = []
    if is_uploaded:
        for student in all_students:
            if student not in matched_students:
                unassigned_students.append(student)

    actual_assignments = []
    if request.method == 'POST':
        name = request.form['name'].strip()
        if not name:
            flash('Please enter a name to search.', 'warning')
        else:
            for assignment in assignments:
                if (name.lower() in assignment['student'].lower() or 
                    name.lower() in assignment['tutor'].lower() or 
                    name.lower() in assignment['subject'].lower() or 
                    name.lower() in assignment['time_slot'].lower()):
                    actual_assignments.append(assignment)

            if len(actual_assignments) == 0:
                flash('No results found.', 'info')
    else:
        actual_assignments = assignments

    return render_template('search.html', 
                         assignments=actual_assignments,
                         unassigned_students=unassigned_students)

@app.route('/download_schedule')
def download_schedule():
    saved_schedule_path = os.path.join(app.config['UPLOAD_FOLDER'], "saved_schedule.csv")
    try:
        return send_file(
            saved_schedule_path,
            mimetype='text/csv',
            as_attachment=True,
            download_name='tutor_schedule.csv'
        )
    except Exception as e:
        flash(f'Error downloading file: {str(e)}', 'error')
        return redirect(url_for('search'))

@app.route('/email', methods=['GET', 'POST'])
def email():
    # Count the number of emails to be sent (from saved_schedule.csv)
    email_count = 0

    if is_uploaded:
        saved_schedule_path = os.path.join(app.config['UPLOAD_FOLDER'], "saved_schedule.csv")
        if os.path.exists(saved_schedule_path):
            df = pd.read_csv(saved_schedule_path)
            email_count = len(df)
            
            if request.method == 'POST':
                for index, row in df.iterrows():
                    student_name = row['Student Name']
                    student_email = "ryu@geffenacademy.ucla.edu"
                    student_grade = row['Student Grade']
                    tutor_name = row['Tutor Name']
                    tutor_email = "ryu@geffenacademy.ucla.edu"
                    tutor_grade = row['Tutor Grade']
                    time_slot = row['Time']
                    subject = row['Student Courses']
                    info = row['Additional Info']

                    # Create Student and Tutor objects
                    student = Student(student_name, student_email, student_grade, None, subject, info, None, None)
                    tutor = Tutor(tutor_name, tutor_email, tutor_grade, None, subject, None)
                    student.matched_tutors = [tutor]
                    tutor.matched_students = [student]

                    # Send emails
                    subject_student = (f'Peer Tutoring Schedule')
                    message_student = (f'Dear {student.name}, \n\nYou have been matched with {tutor.name} for these classes: {subject}. {tutor.name} is available to meet with you at {time_slot}. \n Regards, \n Geffen Peer Tutoring Team')

                    subject_tutor = (f'Peer Tutoring Schedule')
                    message_tutor = (f'Dear {tutor.name}, \n\nYou have been matched with {student.name} for these classes: {subject}. {student.name} is available to meet with you at {time_slot}. \n Student Comments: {info} \n Regards, \n Geffen Peer Tutoring Team')

                    email_matched_student(student, subject_student, message_student)
                    email_matched_tutor(tutor, subject_tutor, message_tutor)
                flash('Successfully sent {} emails!'.format(email_count), 'success')

    return render_template('email.html', email_count=email_count)

if __name__ == '__main__':
    app.run(debug=True)