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

peer_tutors = None
students_classes = None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    global peer_tutors, students_classes
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

                    peer_tutors = pd.read_csv(tutor_path)
                    students_classes = pd.read_csv(student_path)
                    
                    student_assignment, time_assignment = get_tutors(student_path, tutor_path)
                    message = "<div class='assignment-results'>"
                    i = 0
                    for student, tutor in student_assignment.items():
                        message += (
                            f"<div class='match'>{i}"
                            f"<p><strong>Student:</strong> {student.name} ({student.email})</p>"
                            f"<p><strong>Tutor:</strong> {tutor.name} ({tutor.email})</p>"
                            f"<p><strong>Courses:</strong> {', '.join(student.courses)}</p>"
                            f"<p><strong>Time:</strong> {student.final_time}</p>"
                            f"</div><hr>"
                        )
                        i += 1
                    message += "</div>"
                except Exception as e:
                    message = f"Error processing files: {str(e)}"
            else:
                message = "Please select both files"
        else:
            message = "Please upload both required files"

    return render_template('upload.html', message=message)

@app.route('/search', methods=['GET', 'POST'])
def search():
    global peer_tutors, students_classes

    results = []
    if request.method == 'POST':
        name = request.form['name'].strip()
        if not name:
            flash('Please enter a name to search.', 'warning')
        else:
            if peer_tutors is not None and name in peer_tutors.values:
                results.append(f"Peer Tutor Found: {name}")
                
            if students_classes is not None:
                student_data = students_classes[students_classes['Student\'s name: '] == name]
                if not student_data.empty:
                    classes = ", ".join(student_data['Subject (and level if applicable) that the student needs tutoring in: '])
                    results.append(f"Student Found: {name}\nClasses: {classes}")

            if not results:
                flash('No results found.', 'info')
            else:
                flash('\n\n'.join(results), 'success')

    return render_template('search.html')

#CHECK THIS CODE
#email page displays email
@app.route('/email')
def email():

    #if emails sent, send all the emails and display message that emails were sent
    #if emails deleted, delete email from box and display message

    return render_template('email.html')

if __name__ == '__main__':
    app.run(debug=True)