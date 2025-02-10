from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import os

app = Flask(__name__, static_folder='static')

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

peer_tutors = None
students_classes = None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """
    global peer_tutors, students_classes
    if request.method == 'POST':
        if 'peer_tutors_file' in request.files:
            file = request.files['peer_tutors_file']
            if file.filename != '':
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                peer_tutors = pd.read_csv(file_path)
                flash('Peer tutors file uploaded successfully!', 'success')

        if 'students_classes_file' in request.files:
            file = request.files['students_classes_file']
            if file.filename != '':
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                students_classes = pd.read_csv(file_path)
                flash('Students and classes file uploaded successfully!', 'success')
    """

    return render_template('upload.html')

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