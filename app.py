from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
from get_tutors import get_tutors
import os
import random

app = Flask(__name__, static_folder='static')
app.secret_key = '0599db35270c938d478af4964d9c00aa'

# Define upload folder path
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

peer_tutor_responses = None
student_responses = None
student_assignment = None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    global peer_tutor_responses, student_responses, student_assignment
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

                    peer_tutor_responses = pd.read_csv(tutor_path)
                    student_responses = pd.read_csv(student_path)
                    
                    student_assignment, time_assignment = get_tutors(student_path, tutor_path)
                    message = "Files uploaded successfully"
                except Exception as e:
                    message = f"Error processing files: {str(e)}"
            else:
                message = "Please select both files"
        else:
            message = "Please upload both required files"

    return render_template('upload.html', message=message)

@app.route('/search', methods=['GET', 'POST'])
def search():
    global peer_tutor_responses, student_responses, student_assignment
    
    # Convert student_assignment dictionary to a list of dictionaries for the template
    assignments = []
    if (student_assignment is not None):
        for student, tutor in student_assignment.items():
            assignment = {
                'student': student.name,
                'tutor': tutor.name,
                'subject': ",".join(student.courses),
                'time_slot': student.final_time.replace(":", " - ")
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

    return render_template('search.html', assignments=actual_assignments)

#CHECK THIS CODE
#email page displays email
@app.route('/email')
def email():

    #if emails sent, send all the emails and display message that emails were sent
    #if emails deleted, delete email from box and display message

    return render_template('email.html')

if __name__ == '__main__':
    app.run(debug=True)