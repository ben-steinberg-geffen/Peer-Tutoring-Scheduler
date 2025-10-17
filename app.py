from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import pandas as pd
import os
from auto_email import auto_email
from models import Student, Tutor
from persistent_data import save_data, load_data
import re
from save_schedule_assignment import save_schedule_assignment
from data_loader import load_tutor_data, load_student_data

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
    # Load live tutor and student form data to offer choices
    try:
        tutors_df = load_tutor_data()
    except Exception:
        tutors_df = pd.DataFrame(columns=['name', 'email', 'grade', 'courses', 'availability'])
    try:
        students_df = load_student_data()
    except Exception:
        students_df = pd.DataFrame(columns=['name', 'email', 'grade', 'courses', 'availability', 'additional_info'])
    assignments = []
    for idx, row in df.iterrows():
        if row.get('Status') == 'Not Matched':
            continue
        subjects_tutor = row.get('Tutor Courses', '').split(", ")
        subjects_student = row.get('Student Courses', '').split(", ")
        subjects_both = [s for s in subjects_tutor if s in subjects_student]
        # Determine a subject to match tutors against
        subject_for_match = subjects_both[0] if subjects_both else (row.get('Student Courses', '').split(', ')[0] if row.get('Student Courses') else '')

        # Build tutor options: tutors who teach the subject
        tutor_options = []
        time_options = []
        if subject_for_match:
            for _, trow in tutors_df.iterrows():
                t_courses = trow.get('courses', []) if isinstance(trow.get('courses', []), list) else []
                if subject_for_match in t_courses:
                    tutor_options.append({'name': trow.get('name', ''), 'email': trow.get('email', ''), 'availability': trow.get('availability', [])})

        # Get student availability from the form data if available
        student_availability = []
        sname = row.get('Student Name', '')
        if not students_df.empty and sname:
            matches = students_df[students_df['name'] == sname]
            if not matches.empty:
                # If multiple, try to match by course too
                if len(matches) > 1 and row.get('Student Courses'):
                    course = row.get('Student Courses').split(', ')[0]
                    matches = matches[matches['courses'].apply(lambda cs: course in cs if isinstance(cs, list) else False)]
                if not matches.empty:
                    student_availability = matches.iloc[0].get('availability', []) if isinstance(matches.iloc[0].get('availability', []), list) else []

        # Determine intersecting times across tutors and student availability
        if tutor_options and student_availability:
            times_set = set()
            for t in tutor_options:
                t_avail = t.get('availability', []) if isinstance(t.get('availability', []), list) else []
                inter = set(t_avail).intersection(set(student_availability))
                times_set.update(inter)
            time_options = sorted(times_set)

        assignments.append({
            'student': row.get('Student Name', ''),
            'tutor': row.get('Tutor Name', ''),
            'subject': ", ".join(subjects_both),
            'time_slot': row.get('Time', ''),
            'row_index': int(idx),
            'tutor_options': tutor_options,
            'time_options': time_options
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
    saved_links = load_data("links") or {}
    if request.method == 'POST':
        student_link = request.form.get('student_form_link', '').strip()
        tutor_link = request.form.get('tutor_form_link', '').strip()

        def valid_sheet_link(link):
            if not link or 'docs.google.com/spreadsheets' not in link:
                return False
            # accept edit links, export links, or links containing usp= or format=csv
            if '/edit' in link or '/export' in link or 'usp=' in link or 'format=csv' in link:
                return True
            return False

        if not valid_sheet_link(student_link) or not valid_sheet_link(tutor_link):
            flash('Please provide valid Google Sheets links (must be a sheet edit or export link).', 'danger')
            return render_template('setup.html', saved_links=saved_links)

        save_data({"student_link": student_link, "tutor_link": tutor_link}, "links")
        # attempt to refresh the saved schedule from the forms
        try:
            save_schedule_assignment()
            flash('Links saved and schedule refreshed.', 'success')
        except Exception as e:
            flash(f'Links saved but refresh failed: {e}', 'warning')
        # reload saved_links for template
        saved_links = load_data('links') or {}
        return render_template('setup.html', saved_links=saved_links)

    return render_template('setup.html', saved_links=saved_links)

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

@app.route('/modify_assignment', methods=['POST'])
def modify_assignment():
    """Modify or delete an assignment manually."""
    try:
        row_index = int(request.form.get('row_index'))
    except Exception:
        flash('Invalid row index.', 'danger')
        return redirect(url_for('search'))

    action = request.form.get('action')
    if action not in ('delete', 'update'):
        flash('Unknown action.', 'warning')
        return redirect(url_for('search'))

    if not os.path.exists(SCHEDULE_PATH):
        flash('Schedule file not found.', 'danger')
        return redirect(url_for('search'))

    df = pd.read_csv(SCHEDULE_PATH)
    if row_index < 0 or row_index >= len(df):
        flash('Row index out of range.', 'danger')
        return redirect(url_for('search'))

    if action == 'delete':
        # mark as Not Matched
        df.at[row_index, 'Status'] = 'Not Matched'
        df.at[row_index, 'Tutor Name'] = ''
        df.at[row_index, 'Tutor Email'] = ''
        df.at[row_index, 'Time'] = ''
        flash('Assignment deleted (marked Not Matched).', 'success')

    elif action == 'update':
        new_tutor = request.form.get('new_tutor', '').strip()
        new_time = request.form.get('new_time', '').strip()
        # search for the new tutor's email
        if new_tutor:
            df.at[row_index, 'Tutor Name'] = new_tutor
            try:
                tutors_df = load_tutor_data()
                match = tutors_df[tutors_df['name'] == new_tutor]
                if not match.empty:
                    df.at[row_index, 'Tutor Email'] = match.iloc[0].get('email', '')
            except Exception: # leaves old email
                flash('Tutor email search failed.', 'warning')
                pass
        if new_time:
            df.at[row_index, 'Time'] = new_time
        flash('Assignment updated.', 'success')

    df.to_csv(SCHEDULE_PATH, index=False)
    return redirect(url_for('search'))

def generate_email_previews(df):
    previews = []
    for idx, row in df.iterrows():
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
        time_period = time_slot.split(':')[1] if ':' in time_slot else ''
        time_day = time_slot.split(':')[0] if ':' in time_slot else ''

        # Student matched email
        if not student_email_status and student_status == 'Matched':
            if time_period == " H Block (After School)":
                body = (
                    f'Dear {student_name} and {tutor_name},\n\n'
                    f'You two will be working together for one-on-one tutoring for {subject}. '
                    f'Your first meeting will be on {time_slot}. '
                    f'If there is a scheduling conflict, please reply all to this email (so we are all in the loop).\n\n'
                    f'Please come to the meeting prepared.\n\n'
                    f'Please meet outside the academic lab room #317 at the start of H block. '
                    f'If you feel like the space is too loud, you may choose to leave and work in another place on campus.\n\n'
                    f'I will be checking in with both of you afterwards to see how it went. Be on the lookout for a follow-up email from me with a Google Form to get your feedback. '
                    f'Please fill out the form promptly and let me know if you have any other questions!\n\n'
                    f'Student Comments: {info}\n\n'
                    f'Regards,\n'
                    f'Geffen Peer Tutoring Team'
                )
                
            elif time_period == " Lunch":
                body = (
                    f'Dear {student_name} and {tutor_name},\n\n'
                    f'You two will be working together for one-on-one tutoring for {subject}. '
                    f'Your first meeting will be on {time_slot}. '
                    f'If there is a scheduling conflict, please reply all to this email (so we are all in the loop).\n\n'
                    f'Please come to the meeting prepared.\n\n'
                    f'Please meet outside the academic lab room #317 at the start of H block. '
                    f'If you feel like the space is too loud, you may choose to leave and work in another place on campus.\n\n'
                    f'I will be checking in with both of you afterwards to see how it went. Be on the lookout for a follow-up email from me with a Google Form to get your feedback. '
                    f'Please fill out the form promptly and let me know if you have any other questions!\n\n'
                    f'Student Comments: {info}\n\n'
                    f'Regards,\n'
                    f'Geffen Peer Tutoring Team'
                )
            elif time_period == " Before School":
                body = (
                    f'Dear {student_name} and {tutor_name},\n\n'
                    f'You two will be working together for one on one tutoring for {subject}. '
                    f'Your first meeting will be on {time_slot}. '
                    f'If there is a scheduling conflict, please reply all to this email (so we are all in the loop).\n\n'
                    f'Please come to the meeting prepared with questions for your tutor or an assignment that you would like to go over.\n\n'
                    f'Please meet outside the academic lab room #317 at 8:15am. '
                    f'If you feel like the space is too loud, you may choose to leave and work in another place on campus.\n\n'
                    f'I will be checking in with both of you afterwards to see how it went. Be on the lookout for a follow-up email from me '
                    f'with a Google Form to get your feedback. Please fill out the form promptly and let me know if you have any other questions!'
                    f'Student Comments: {info}\n\n'
                    f'Regards,\n'
                    f'Geffen Peer Tutoring Team'
                )
            else:
                body = (
                    f'Dear {student_name} and {tutor_name},\n\n'
                    f'You two will be working together for one-on-one tutoring for {subject}. '
                    f'Your first meeting will be on {time_slot}. '
                    f'If there is a scheduling conflict, please reply all to this email (so we are all in the loop).\n\n'
                    f'Please come to the meeting prepared.\n\n'
                    f'Please meet outside the academic lab room #317 at the meeting. '
                    f'If you feel like the space is too loud, you may choose to leave and work in another place on campus.\n\n'
                    f'I will be checking in with both of you afterwards to see how it went. Be on the lookout for a follow-up email from me with a Google Form to get your feedback. '
                    f'Please fill out the form promptly and let me know if you have any other questions!\n\n'
                    f'Student Comments: {info}\n\n'
                    f'Regards,\n'
                    f'Geffen Peer Tutoring Team'
                )

            previews.append({
                'recipient_type': 'Student',
                'recipient_name': student_name,
                'recipient_email': row.get('Student Email', ''),
                'subject': 'Peer Tutoring Schedule',
                'body': body,
                'row_index': idx
                })

        # Student not matched email
        if not student_email_status and student_status == 'Not Matched':
            body = (f'Dear {student_name},\n\nUnfortunately, we have not been able to match you with a tutor for your selected course: {subject} because {reason}.\n\n'
                    f'Here are possible time slots you could consider: {potential_times}\n\nRegards,\nGeffen Peer Tutoring Team') if potential_times != '[]' else \
                    (f'Dear {student_name},\n\nUnfortunately, we have not been able to match you with a tutor because {reason}.\n\nRegards,\nGeffen Peer Tutoring Team')
            previews.append({
                'recipient_type': 'Student',
                'recipient_name': student_name,
                'recipient_email': row.get('Student Email', ''),
                'subject': 'Peer Tutoring Arrangement',
                'body': body,
                'row_index': idx
            })
        
        # Tutor matched email
        if not tutor_email_status and student_status == 'Matched':
            if time_period == " H Block (After School)":
                body = (
                    f'Dear {student_name} and {tutor_name},\n\n'
                    f'You two will be working together for one-on-one tutoring for {subject}. '
                    f'Your first meeting will be on {time_slot}. '
                    f'If there is a scheduling conflict, please reply all to this email (so we are all in the loop).\n\n'
                    f'Please come to the meeting prepared.\n\n'
                    f'Please meet outside the academic lab room #317 at the start of H block. '
                    f'If you feel like the space is too loud, you may choose to leave and work in another place on campus.\n\n'
                    f'I will be checking in with both of you afterwards to see how it went. Be on the lookout for a follow-up email from me with a Google Form to get your feedback. '
                    f'Please fill out the form promptly and let me know if you have any other questions!\n\n'
                    f'Student Comments: {info}\n\n'
                    f'Regards,\n'
                    f'Geffen Peer Tutoring Team'
                )
            elif time_period == " Lunch":
                body = (
                    f'Dear {student_name} and {tutor_name},\n\n'
                    f'You two will be working together for one-on-one tutoring for {subject}. '
                    f'Your first meeting will be on {time_slot}. '
                    f'If there is a scheduling conflict, please reply all to this email (so we are all in the loop).\n\n'
                    f'Please come to the meeting prepared.\n\n'
                    f'Please meet outside the academic lab room #317 at the start of H block. '
                    f'If you feel like the space is too loud, you may choose to leave and work in another place on campus.\n\n'
                    f'I will be checking in with both of you afterwards to see how it went. Be on the lookout for a follow-up email from me with a Google Form to get your feedback. '
                    f'Please fill out the form promptly and let me know if you have any other questions!\n\n'
                    f'Student Comments: {info}\n\n'
                    f'Regards,\n'
                    f'Geffen Peer Tutoring Team'
                )
            elif time_period == " Before School":
                body = (
                    f'Dear {student_name} and {tutor_name},\n\n'
                    f'You two will be working together for one on one tutoring for {subject}. '
                    f'Your first meeting will be on {time_slot}. '
                    f'If there is a scheduling conflict, please reply all to this email (so we are all in the loop).\n\n'
                    f'Please come to the meeting prepared with questions for your tutor or an assignment that you would like to go over.\n\n'
                    f'Please meet outside the academic lab room #317 at 8:15am. '
                    f'If you feel like the space is too loud, you may choose to leave and work in another place on campus.\n\n'
                    f'I will be checking in with both of you afterwards to see how it went. Be on the lookout for a follow-up email from me '
                    f'with a Google Form to get your feedback. Please fill out the form promptly and let me know if you have any other questions!'
                    f'Student Comments: {info}\n\n'
                    f'Regards,\n'
                    f'Geffen Peer Tutoring Team'
                )
            else:
                body = (
                    f'Dear {student_name} and {tutor_name},\n\n'
                    f'You two will be working together for one-on-one tutoring for {subject}. '
                    f'Your first meeting will be on {time_slot}. '
                    f'If there is a scheduling conflict, please reply all to this email (so we are all in the loop).\n\n'
                    f'Please come to the meeting prepared.\n\n'
                    f'Please meet outside the academic lab room #317 at the meeting. '
                    f'If you feel like the space is too loud, you may choose to leave and work in another place on campus.\n\n'
                    f'I will be checking in with both of you afterwards to see how it went. Be on the lookout for a follow-up email from me with a Google Form to get your feedback. '
                    f'Please fill out the form promptly and let me know if you have any other questions!\n\n'
                    f'Student Comments: {info}\n\n'
                    f'Regards,\n'
                    f'Geffen Peer Tutoring Team'
                )
            previews.append({
                'recipient_type': 'Tutor',
                'recipient_name': tutor_name,
                'recipient_email': row.get('Tutor Email', ''),
                'subject': 'Peer Tutoring Schedule',
                'body': body,
                'row_index': idx
                })            

    return previews


def generate_sent_previews(df):
    """Return previews for emails already sent (Student Email Status or Tutor Email Status == True)."""
    sent = []
    for idx, row in df.iterrows():
        student_name = str(row.get('Student Name', 'N/A'))
        tutor_name = str(row.get('Tutor Name', 'N/A'))
        subject = str(row.get('Student Courses', 'N/A'))
        time_slot = str(row.get('Time', 'N/A'))
        info = str(row.get('Additional Info', ''))
        student_status = str(row.get('Status', ''))
        # only include sent items for matched pairs
        if student_status != 'Matched':
            continue

        # build a similar body as generate_email_previews for matched case
        time_period = time_slot.split(':')[1] if ':' in time_slot else ''
        time_day = time_slot.split(':')[0] if ':' in time_slot else ''

        # Prefer saved sent subject/body if present
        # Student
        if bool(row.get('Student Email Status', False)):
            subj = row.get('Student Last Sent Subject') if 'Student Last Sent Subject' in row.index else None
            body_text = row.get('Student Last Sent Body') if 'Student Last Sent Body' in row.index else None
            if not subj or not body_text:
                subj = f'Peer Tutoring Schedule'
                body_text = (f'Dear {student_name} and {tutor_name},\n\nYou two will be working together for one-on-one tutoring for {subject}. Your first meeting will be on {time_slot}.')
            sent.append({
                'recipient_type': 'Student',
                'recipient_name': student_name,
                'subject': subj,
                'body': body_text,
                'row_index': idx
            })

        # Tutor
        if bool(row.get('Tutor Email Status', False)):
            subj = row.get('Tutor Last Sent Subject') if 'Tutor Last Sent Subject' in row.index else None
            body_text = row.get('Tutor Last Sent Body') if 'Tutor Last Sent Body' in row.index else None
            if not subj or not body_text:
                subj = f'Peer Tutoring Schedule'
                body_text = (f'Dear {student_name} and {tutor_name},\n\nYou two will be working together for one-on-one tutoring for {subject}. Your first meeting will be on {time_slot}.')
            sent.append({
                'recipient_type': 'Tutor',
                'recipient_name': tutor_name,
                'subject': subj,
                'body': body_text,
                'row_index': idx
            })

    return sent

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
    sent_previews = generate_sent_previews(df)
    email_count = int((~df['Student Email Status']).sum() + (~df['Tutor Email Status']).sum())

    def persist_sent(df_local, row_index, recipient, subject, body):
        """Save exact sent subject/body into dataframe columns for recipient ('Student' or 'Tutor')."""
        subj_col = f"{recipient} Last Sent Subject"
        body_col = f"{recipient} Last Sent Body"
        if subj_col not in df_local.columns:
            df_local[subj_col] = ''
        if body_col not in df_local.columns:
            df_local[body_col] = ''
        df_local.at[row_index, subj_col] = subject
        df_local.at[row_index, body_col] = body
        return df_local

    if request.method == 'POST':
        send_count = 0
        try:
            # one at a time send
            if request.form.get('single_send'):
                try:
                    idx = int(request.form.get('row_index'))
                except Exception:
                    flash('Invalid row index for single send.', 'danger')
                    return redirect(url_for('email'))

                recipient_type = request.form.get('recipient_type', 'Student')
                if idx < 0 or idx >= len(df):
                    flash('Row index out of range.', 'danger')
                    return redirect(url_for('email'))

                row = df.iloc[idx]

                student = Student(
                    row.get('Student Name', ''), row.get('Student Email', ''), row.get('Student Grade', ''),
                    None, row.get('Student Courses', ''), row.get('Additional Info', ''), None, True, None
                )
                tutor = Tutor(
                    row.get('Tutor Name', ''), row.get('Tutor Email', ''), row.get('Tutor Grade', ''),
                    None, row.get('Student Courses', ''), None, True
                )
                tutor.matched_students = [student]
                student.matched_tutors = [tutor]

                subj = request.form.get('subject', 'Peer Tutoring Schedule')
                body = request.form.get('body', '')
                try:
                    if recipient_type == 'Student':
                        if not row.get('Student Email Status', False):
                            auto_email(student, subj, body)
                            df.at[idx, 'Student Email Status'] = True
                            df = persist_sent(df, idx, 'Student', subj, body)
                            send_count = 1
                    else:
                        if not row.get('Tutor Email Status', False):
                            auto_email(tutor, subj, body)
                            df.at[idx, 'Tutor Email Status'] = True
                            df = persist_sent(df, idx, 'Tutor', subj, body)
                            send_count = 1
                except Exception as e:
                    flash(f'Error sending email: {e}', 'danger')
                    return redirect(url_for('email'))

            # Send all
            elif request.form.get('send_all'):
                for preview in email_previews:
                    idx = preview['row_index']
                    row = df.iloc[idx]

                    student = Student(
                        row.get('Student Name', ''), row.get('Student Email', ''), row.get('Student Grade', ''),
                        None, row.get('Student Courses', ''), row.get('Additional Info', ''), None, True, None
                    )
                    tutor = Tutor(
                        row.get('Tutor Name', ''), row.get('Tutor Email', ''), row.get('Tutor Grade', ''),
                        None, row.get('Student Courses', ''), None, True
                    )
                    tutor.matched_students = [student]
                    student.matched_tutors = [tutor]

                    subj = preview.get('subject', 'Peer Tutoring Schedule')
                    body = preview.get('body', '')
                    try:
                        if preview['recipient_type'] == 'Student':
                            if not row.get('Student Email Status', False):
                                auto_email(student, subj, body)
                                df.at[idx, 'Student Email Status'] = True
                                df = persist_sent(df, idx, 'Student', subj, body)
                                send_count += 1
                        elif preview['recipient_type'] == 'Tutor':
                            if not row.get('Tutor Email Status', False):
                                auto_email(tutor, subj, body)
                                df.at[idx, 'Tutor Email Status'] = True
                                df = persist_sent(df, idx, 'Tutor', subj, body)
                                send_count += 1
                    except Exception as e:
                        # continue on errors but report
                        flash(f'Error sending to row {idx}: {e}', 'warning')

            else:
                flash('Unknown action.', 'warning')
                return redirect(url_for('email'))

            df.to_csv(SCHEDULE_PATH, index=False)
            flash(f'Successfully sent {send_count} emails!', 'success')
            return redirect(url_for('email'))
        except Exception as e:
            flash(f'An error occurred during email sending: {e}', 'danger')
            return render_template('email.html', email_count=email_count, previews=email_previews)

    return render_template('email.html', email_count=email_count, previews=email_previews, sent_previews=sent_previews)

if __name__ == '__main__':
    import webbrowser
    webbrowser.open_new('http://127.0.0.1:5000/') 
    
    app.run(debug=False)
