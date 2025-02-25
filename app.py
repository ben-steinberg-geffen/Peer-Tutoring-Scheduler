from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import pandas as pd
from get_tutors import get_schedule
import os
import random

app = Flask(__name__, static_folder='static')
app.secret_key = '0599db35270c938d478af4964d9c00aa'

# Define upload folder path
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

is_uploaded = False

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    global is_uploaded
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
    global is_uploaded
    
    saved_schedule_path = os.path.join(app.config['UPLOAD_FOLDER'], "saved_schedule.csv")
    data = pd.read_csv(saved_schedule_path)
    # Get the column headers from the DataFrame
    headers = list(data.columns)

    # Convert DataFrame rows to a list of dictionaries for the template
    assignments = []
    for index, row in data.iterrows():
        subjects_tutor =  row['Tutor Courses'].split(", ")
        subjects_student = row['Student Courses'].split(", ")
        subjects_both = []
        for subject in subjects_tutor:
            if subject in subjects_student:
                subjects_both.append(subject)
        assignment = {
            'student': row['Student Name'] if 'Student Name' in row else row[0],  # Fallback to first column if header not found
            'tutor': row['Tutor Name'] if 'Tutor Name' in row else row[1],       # Fallback to second column if header not found
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
                         unassigned={})

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

#CHECK THIS CODE
#email page displays email
@app.route('/email')
def email():

    #if emails sent, send all the emails and display message that emails were sent
    #if emails deleted, delete email from box and display message

    return render_template('email.html')

if __name__ == '__main__':
    app.run(debug=True)
