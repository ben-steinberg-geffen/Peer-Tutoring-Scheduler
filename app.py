from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import pandas as pd
import os
from auto_email import auto_email
from models import Student, Tutor
from persistent_data import save_data, load_data
from save_schedule_assignment import save_schedule_assignment

app = Flask(__name__, static_folder='static')
app.secret_key = '0599db35270c938d478af4964d9c00aa'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'data', 'uploads')
SCHEDULE_PATH = os.path.join(BASE_DIR, "saved_schedule.csv")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_unassigned_students(schedule_path):
    if not os.path.exists(schedule_path):
        return set()
    df = pd.read_csv(schedule_path)
    if 'Status' in df.columns and 'Student Name' in df.columns:
        return set(df[df['Status'] == 'Not Matched']['Student Name'].tolist())
    return set()

def load_assignments(schedule_path):
    if not os.path.exists(schedule_path):
        return []
    df = pd.read_csv(schedule_path)
    assignments = []
    for _, row in df.iterrows():
        if row.get('Status') == 'Not Matched':
            continue
        subjects_tutor = row.get('Tutor Courses', '').split(", ")
        subjects_student = row.get('Student Courses', '').split(", ")
        subjects_both = [s for s in subjects_tutor if s in subjects_student]
        assignments.append({
            'student': row.get('Student Name', ''),
            'tutor': row.get('Tutor Name', ''),
            'subject': ", ".join(subjects_both),
            'time_slot': row.get('Time', '')
        })
    assignments.sort(key=lambda x: (x['tutor'].lower(), x['student'].lower()))
    return assignments

def fill_missing_columns(df, columns, default=''):
    for col in columns:
        if col not in df.columns:
            df[col] = default
        else:
            df[col] = df[col].fillna(default)
    return df

def fill_email_status(df, col):
    if col not in df.columns:
        df[col] = False
    else:
        df[col] = df[col].fillna(False).astype(bool)
    return df

@app.route('/')
def home():
    """Home page."""
    return render_template('home.html')

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    """Setup page for entering form links."""
    message = load_data("links")
    message = message["student_link"] if message else None
    if request.method == 'POST':
        student_link = request.form.get('student_form_link')
        tutor_link = request.form.get('tutor_form_link')
        save_data({"student_link": student_link, "tutor_link": tutor_link}, "links")
        save_schedule_assignment()
    return render_template('setup.html', message=message)

@app.route('/search', methods=['GET', 'POST'])
def search():
    """Search for assignments."""
    assignments = load_assignments(SCHEDULE_PATH)
    actual_assignments = assignments
    if request.method == 'POST':
        name = request.form['name'].strip()
        if not name:
            flash('Please enter a name to search.', 'warning')
        else:
            actual_assignments = [
                a for a in assignments
                if any(name.lower() in str(a[field]).lower() for field in ['student', 'tutor', 'subject', 'time_slot'])
            ]
            if not actual_assignments:
                flash('No results found.', 'info')
    unassigned_students = get_unassigned_students(SCHEDULE_PATH)
    return render_template('search.html',
                           assignments=actual_assignments,
                           unassigned_students=unassigned_students)

@app.route('/download_schedule')
def download_schedule():
    """Download the schedule CSV."""
    try:
        return send_file(
            SCHEDULE_PATH,
            mimetype='text/csv',
            as_attachment=True,
            download_name='tutor_schedule.csv'
        )
    except Exception as e:
        flash(f'Error downloading file: {str(e)}', 'error')
        return redirect(url_for('search'))

def generate_email_previews(df):
    previews = []
    for _, row in df.iterrows():
        student_name = str(row.get('Student Name', 'N/A'))
        tutor_name = str(row.get('Tutor Name', 'N/A'))
        subject = str(row.get('Student Courses', 'N/A'))
        time_slot = str(row.get('Time', 'N/A'))
        info = str(row.get('Additional Info', ''))
        student_status = str(row.get('Status', ''))
        reason = str(row.get('Reason', ''))
        potential_times = str(row.get('Potential Times', '[]'))
        student_email_status = bool(row.get('Student Email Status', False))
        tutor_email_status = bool(row.get('Tutor Email Status', False))
        time_period = time_slot.split(':')[1]

        if not student_email_status and student_status == 'Matched':
            if time_period == " H Block (After School)":
                body = (
                        f'Dear {student_name},\n\n'
                        f'You and {student_name} be working together for one-on-one tutoring for {subject or "the subject"} during {time_slot or "the scheduled time"}. '
                        f'Your first meeting will be {time_period or "on the assigned date"}. '
                        f'If there is a scheduling conflict, please reply all to this email (so we are all in the loop).\n\n'
                        f'Please come to the meeting prepared .\n\n'
                        f'Please meet outside the academic lab room #317 at the start of H block.'
                        f'If you feel like the space is too loud, you may choose to leave and work in another place on campus.\n\n'
                        f'I will be checking in with both of you afterwards to see how it went—be on the lookout for a follow-up email from me with a Google Form to get your feedback. '
                        f'Please fill out the form promptly and let me know if you have any other questions!\n\n'
                        f'Student Comments: {info}\n\n'
                        f'Regards,\n'
                        f'Geffen Peer Tutoring Team'
                                )
            previews.append({
                'recipient_type': 'Student',
                'recipient_name': student_name,
                'subject': 'Peer Tutoring Schedule',
                'body': body
                })

        if not student_email_status and student_status == 'Not Matched':
            body = (f'Dear {student_name},\n\nUnfortunately, we have not been able to match you with a tutor for your selected course: {subject} because {reason}.\n\n'
                    f'Here are possible time slots you could consider: {potential_times}\n\nRegards,\nGeffen Peer Tutoring Team') if potential_times != '[]' else \
                   (f'Dear {student_name},\n\nUnfortunately, we have not been able to match you with a tutor because {reason}.\n\nRegards,\nGeffen Peer Tutoring Team')
            previews.append({
                'recipient_type': 'Student',
                'recipient_name': student_name,
                'subject': 'Peer Tutoring Arrangement',
                'body': body
            })
        if not tutor_email_status and student_status == 'Matched':
            body = (f'Dear {tutor_name},\n\nYou have been matched with {student_name} for these classes: {subject}. {student_name} is available to meet with you at {time_slot}.\n\n'
                    f'Student Comments: {info}\n\nRegards,\nGeffen Peer Tutoring Team') if info and "nan" not in info.lower() else \
                   (f'Dear {tutor_name},\n\nYou have been matched with {student_name} for these classes: {subject}. {student_name} is available to meet with you at {time_slot}.\n\nRegards,\nGeffen Peer Tutoring Team')
            previews.append({
                'recipient_type': 'Tutor',
                'recipient_name': tutor_name,
                'subject': 'Peer Tutoring Schedule',
                'body': body
            })
    return previews

@app.route('/email', methods=['GET', 'POST'])
def email():
    """Preview and send emails to students and tutors."""
    if not os.path.exists(SCHEDULE_PATH):
        flash('Error: saved_schedule.csv not found.', 'danger')
        return render_template('email.html', email_count=0, previews=[])

    try:
        df = pd.read_csv(SCHEDULE_PATH)
        cols_to_fill = ['Student Name', 'Tutor Name', 'Student Courses', 'Time', 'Additional Info', 'Student Grade', 'Tutor Grade']
        df = fill_missing_columns(df, cols_to_fill)
        df = fill_email_status(df, 'Student Email Status')
        df = fill_email_status(df, 'Tutor Email Status')
    except Exception as e:
        flash(f'Error reading or processing CSV: {e}', 'danger')
        return render_template('email.html', email_count=0, previews=[])

    email_previews = generate_email_previews(df)
    email_count = sum(~df['Student Email Status']) + sum(~df['Tutor Email Status'])

    if request.method == 'POST':
        send_count = 0
        try:
            for index, row in df.iterrows():
                student = Student(
                    row['Student Name'], row['Student Email'], row['Student Grade'],
                    None, row['Student Courses'], row['Additional Info'], None, True, None
                )
                tutor = Tutor(
                    row['Tutor Name'], row['Tutor Email'], row['Tutor Grade'],
                    None, row['Student Courses'], None, True
                )
                tutor.matched_students = [student]
                student.matched_tutors = [tutor]

                status = row['Status']
                reason = row.get('Reason', '')
                potential_times = row.get('Potential Times', '')
                info = row.get('Additional Info', '')
                subject = row.get('Student Courses', '')
                time_slot = row.get('Time', '')

                if status == 'Matched':
                    if not row['Student Email Status']:
                        auto_email(student, 'Peer Tutoring Schedule',
                                   f'Dear {student.name}, \n\nYou have been matched with {tutor.name} for these classes: {subject}. {tutor.name} is available to meet with you at {time_slot}. \nRegards, \nGeffen Peer Tutoring Team')
                        df.at[index, 'Student Email Status'] = True
                        send_count += 1
                    if not row['Tutor Email Status']:
                        body = (f'Dear {tutor.name}, \n\nYou have been matched with {student.name} for these classes: {subject}. {student.name} is available to meet with you at {time_slot}.\n\nStudent Comments: {info} \n\nRegards, \nGeffen Peer Tutoring Team') \
                            if "nan" not in str(info).lower() else \
                            (f'Dear {tutor.name}, \n\nYou have been matched with {student.name} for these classes: {subject}. {student.name} is available to meet with you at {time_slot}.\n\nRegards, \nGeffen Peer Tutoring Team')
                        auto_email(tutor, 'Peer Tutoring Schedule', body)
                        df.at[index, 'Tutor Email Status'] = True
                        send_count += 1
                elif status == 'Not Matched':
                    body = (f'Dear {student.name}, \n\nUnfortunately, we have not been able to match you with a tutor because {reason}. \n\nRegards, \nGeffen Peer Tutoring Team') \
                        if potential_times == [] else \
                        (f'Dear {student.name}, \n\nUnfortunately, we have not been able to match you with a tutor because {reason}. \n\nHere are possible time slots you could consider: {potential_times}\n\nRegards, \nGeffen Peer Tutoring Team')
                    auto_email(student, 'Peer Tutoring Arrangement', body)
                    send_count += 1

            df.to_csv(SCHEDULE_PATH, index=False)
            flash(f'Successfully sent {send_count} emails!', 'success')
            return redirect(url_for('email'))
        except Exception as e:
            flash(f'An error occurred during email sending: {e}', 'danger')
            return render_template('email.html', email_count=email_count, previews=email_previews)

    return render_template('email.html', email_count=email_count, previews=email_previews)

if __name__ == '__main__':
    app.run(debug=True)