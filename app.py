from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import pandas as pd
import os
import random
from auto_email import auto_email
from models import Student, Tutor
from scheduler import match_students_tutors, get_not_matched
from persistent_data import save_data, load_data
from save_schedule_assignment import load_student_data, load_tutor_data, split_student_data, save_schedule_assignment, load_existing_schedule
from data_loader import update_students_tutors

app = Flask(__name__, static_folder='static')
app.secret_key = '0599db35270c938d478af4964d9c00aa'
# Define upload folder path
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

is_uploaded = False
all_students = []

student_df = load_student_data()
student_df = split_student_data(student_df)
tutor_df = load_tutor_data()

# Initialize students and tutors
students = []
tutors = []

for _, row in student_df.iterrows():
    students.append(Student(row['name'], row['email'], row['grade'], row['availability'], row['courses'], row['additional_info'], []))

for _, row in tutor_df.iterrows():
    tutors.append(Tutor(row['name'], row['email'], row['grade'], row['availability'], row['courses'], []))

# Load existing schedule if any

if os.path.exists('tutoring_schedule.csv'):
    student_assignment, time_assignment = load_existing_schedule('tutoring_schedule.csv', students, tutors)
else:
    student_assignment, time_assignment = {}, {}

# Update students and tutors with new data
students, tutors = update_students_tutors(student_df, tutor_df, student_assignment)
students, tutors = match_students_tutors(students, tutors)
not_matched = get_not_matched(students, tutors)

students, tutors = update_students_tutors(student_df, tutor_df, student_assignment)
not_matched_students = get_not_matched(students, tutors)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    message = load_data("links")
    if  message is not None:
        message = message["student_link"]
    if request.method == 'POST':
        student_sheet_link = request.form.get('student_form_link')
        tutor_sheet_link = request.form.get('tutor_form_link')

        data = {"student_link": student_sheet_link, "tutor_link": tutor_sheet_link}
        save_data(data, "links")
        save_schedule_assignment()
        pass

    return render_template('setup.html', message=message)

@app.route('/search', methods=['GET', 'POST'])
def search():
    # Convert DataFrame rows to a list of dictionaries for the template
    assignments = []
    matched_students = []
    unassigned_students = set(not_matched_students.keys())
    script_dir = os.path.dirname(os.path.abspath(__file__))
    saved_schedule_path = os.path.join(script_dir, "saved_schedule.csv")
    if os.path.exists(saved_schedule_path):
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
                'tutor': row['Tutor Name'] if 'Tutor Name' in row else row[1],  # Fallback to second column if header not found
                'subject': ", ".join(subjects_both),
                'time_slot': row['Time'] if 'Time' in row else ''
            }
            assignments.append(assignment)

    # Sort the assignments list by tutor name first, then student name
    assignments.sort(key=lambda x: (x['tutor'].lower(), x['student'].lower()))


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
    assignments = []  # List to store all assignments for preview
    

    script_dir = os.path.dirname(os.path.abspath(__file__))
    saved_schedule_path = os.path.join(script_dir, "saved_schedule.csv")
    
    if os.path.exists(saved_schedule_path):
        df = pd.read_csv(saved_schedule_path)
        email_count = len(df) * 2 + len(not_matched_students)

        # Create preview data
        for _, row in df.iterrows():
            assignment = {
                'student': row['Student Name'],
                'tutor': row['Tutor Name'],
                'subject': row['Student Courses'],
                'time_slot': row['Time'],
                'additional_info': row['Additional Info']
            }
            assignments.append(assignment)

        if request.method == 'POST':
            for index, row in df.iterrows():
                student_name = row['Student Name']
                student_email = "hliao38@geffenacademy.ucla.edu"
                student_grade = row['Student Grade']
                tutor_name = row['Tutor Name']
                tutor_email = "hliao38@geffenacademy.ucla.edu"
                tutor_grade = row['Tutor Grade']
                time_slot = row['Time']
                subject = row['Student Courses']
                info = row['Additional Info']
                email_status = row['Student Email Status']
                tutor_email_status = row['Tutor Email Status']

                student = Student(student_name, student_email, student_grade, None, subject, info, None, True, None)
                tutor = Tutor(tutor_name, tutor_email, tutor_grade, None, subject, None, True)
                tutor.matched_students = [student]
                student.matched_tutors = [tutor]

                if email_status == False:
                    subject_student = (f'Peer Tutoring Schedule')
                    message_student = (f'Dear {student.name}, \n\nYou have been matched with {tutor.name} for these classes: {subject}. {tutor.name} is available to meet with you at {time_slot}. \nRegards, \nGeffen Peer Tutoring Team')
                    
                    auto_email(student, subject_student, message_student)
                    df.at[index, 'Student Email Status'] = True  # Update email status in DataFrame

                if tutor_email_status == False:
                    subject_tutor = (f'Peer Tutoring Schedule')

                    if "nan" not in str(info).lower():
                        message_tutor = (f'Dear {tutor.name}, \n\nYou have been matched with {student.name} for these classes: {subject}. {student.name} is available to meet with you at {time_slot}.\n\nStudent Comments: {info} \n\nRegards, \nGeffen Peer Tutoring Team')
                    else:
                        message_tutor = (f'Dear {tutor.name}, \n\nYou have been matched with {student.name} for these classes: {subject}. {student.name} is available to meet with you at {time_slot}.\n\nRegards, \nGeffen Peer Tutoring Team')

                    auto_email(tutor, subject_tutor, message_tutor)                    
                    df.at[index, 'Tutor Email Status'] = True  # Update email status in DataFrame
                
            for student in not_matched_students.keys():
                subject_student = (f'Peer Tutoring Arrangement')
                student.email = "hliao38@geffenacademy.ucla.edu"
                if not not_matched_students[student][1]:
                    message_student = (f'Dear {student.name}, \n\nUnfortunately, we have not been able to match you with a tutor because {not_matched_students[student][0]}. \n\nRegards, \nGeffen Peer Tutoring Team')
                else:
                    message_student = (f'Dear {student.name}, \n\nUnfortunately, we have not been able to match you with a tutor because {not_matched_students[student][0]}. \n\nHere are possible time slots you could consider: {not_matched_students[student][1]}\n\nRegards, \nGeffen Peer Tutoring Team')
                auto_email(student, subject_student, message_student)

            # Save the updated DataFrame back to the CSV file
            df.to_csv(saved_schedule_path, index=False)
            flash('Successfully sent {} emails!'.format(email_count), 'success')

    return render_template('email.html', email_count=email_count, assignments=assignments)

if __name__ == '__main__':
    app.run(debug=True)