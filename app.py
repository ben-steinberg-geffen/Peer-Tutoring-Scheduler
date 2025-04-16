from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import pandas as pd
import os
import random
from auto_email import auto_email
from models import Student, Tutor
from persistent_data import save_data, load_data
from save_schedule_assignment import save_schedule_assignment

app = Flask(__name__, static_folder='static')
app.secret_key = '0599db35270c938d478af4964d9c00aa'
# Define upload folder path
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

is_uploaded = False
all_students = []

script_dir = os.path.dirname(os.path.abspath(__file__))
saved_schedule_path = os.path.join(script_dir, "saved_schedule.csv")
if os.path.exists(saved_schedule_path):
    df = pd.read_csv(saved_schedule_path)
    not_matched = df[df['Status'] == 'Not Matched']
    not_matched_students = set(not_matched['Student Name'].tolist())
    unassigned_students = not_matched_students
    for student in unassigned_students: 
        print("student: ", student)



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
    script_dir = os.path.dirname(os.path.abspath(__file__))
    saved_schedule_path = os.path.join(script_dir, "saved_schedule.csv")
    if os.path.exists(saved_schedule_path):
        data = pd.read_csv(saved_schedule_path)
        # Get the column headers from the DataFrame
        for index, row in data.iterrows():
            if row['Status'] == 'Not Matched':
                continue
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
    email_previews = [] # List to store preview data for the template
    email_count = 0     # Counter for emails that *will* be sent

    script_dir = os.path.dirname(os.path.abspath(__file__))
    saved_schedule_path = os.path.join(script_dir, "saved_schedule.csv")

    if not os.path.exists(saved_schedule_path):
        flash('Error: saved_schedule.csv not found.', 'danger')
        return render_template('email.html', email_count=0, previews=[])

    try:
        df = pd.read_csv(saved_schedule_path)
        # *** FIX for NaN: Fill NaN in relevant columns with empty strings ***
        # Adjust columns if needed based on your actual CSV headers
        cols_to_fill = ['Student Name', 'Tutor Name', 'Student Courses', 'Time', 'Additional Info', 'Student Grade', 'Tutor Grade']
        # Ensure columns exist before filling
        for col in cols_to_fill:
            if col in df.columns:
                df[col] = df[col].fillna('')
            else:
                print(f"Warning: Column '{col}' not found in CSV. Skipping NaN fill for it.")
                # Optionally create the column with empty strings if it's critical
                # df[col] = '' 

        # Ensure Status columns exist and are boolean, fill NaN with False
        if 'Student Email Status' in df.columns:
             df['Student Email Status'] = df['Student Email Status'].fillna(False).astype(bool)
        else:
            print("Warning: Column 'Student Email Status' not found. Assuming all need emails.")
            df['Student Email Status'] = False # Create it if missing

        if 'Tutor Email Status' in df.columns:
            df['Tutor Email Status'] = df['Tutor Email Status'].fillna(False).astype(bool)
        else:
            print("Warning: Column 'Tutor Email Status' not found. Assuming all need emails.")
            df['Tutor Email Status'] = False # Create it if missing
            

    except Exception as e:
        flash(f'Error reading or processing CSV: {e}', 'danger')
        return render_template('email.html', email_count=0, previews=[])

    # --- Logic for GET request (Generate Previews) ---
    for index, row in df.iterrows():
        # Extract data safely using .get() with defaults or direct access after fillna
        student_name = str(row.get('Student Name', 'N/A'))
        tutor_name = str(row.get('Tutor Name', 'N/A'))
        subject = str(row.get('Student Courses', 'N/A'))
        time_slot = str(row.get('Time', 'N/A'))
        info = str(row.get('Additional Info', '')) # Keep info as string, handle emptiness later
        student_email_status = bool(row.get('Student Email Status', False))
        tutor_email_status = bool(row.get('Tutor Email Status', False))

        # Generate preview for Student if email not sent
        if not student_email_status:
            email_count += 1
            subject_student = f'Peer Tutoring Schedule'
            # Use f-string directly, checking for empty names just in case
            message_student = (f'Dear {student_name or "Student"},\n\n'
                               f'You have been matched with {tutor_name or "a tutor"} for these classes: {subject or "specified subjects"}. '
                               f'{tutor_name or "Your tutor"} is available to meet with you at {time_slot or "the scheduled time"}.\n\n'
                               f'Regards,\n'
                               f'Geffen Peer Tutoring Team')
            email_previews.append({
                'recipient_type': 'Student',
                'recipient_name': student_name or "Unknown Student",
                'subject': subject_student,
                'body': message_student
            })

        # Generate preview for Tutor if email not sent
        if not tutor_email_status:
            email_count += 1
            subject_tutor = f'Peer Tutoring Schedule'
            # Conditional message based on 'info'
            # Check if info is not empty AND does not contain 'nan' (case-insensitive)
            # The check for 'nan' might be redundant after fillna('') but kept for safety
            if info and "nan" not in info.lower():
                 message_tutor = (f'Dear {tutor_name or "Tutor"},\n\n'
                                 f'You have been matched with {student_name or "a student"} for these classes: {subject or "specified subjects"}. '
                                 f'{student_name or "The student"} is available to meet with you at {time_slot or "the scheduled time"}.\n\n'
                                 f'Student Comments: {info}\n\n'
                                 f'Regards,\n'
                                 f'Geffen Peer Tutoring Team')
            else:
                 message_tutor = (f'Dear {tutor_name or "Tutor"},\n\n'
                                 f'You have been matched with {student_name or "a student"} for these classes: {subject or "specified subjects"}. '
                                 f'{student_name or "The student"} is available to meet with you at {time_slot or "the scheduled time"}.\n\n'
                                 f'Regards,\n'
                                 f'Geffen Peer Tutoring Team')
            email_previews.append({
                'recipient_type': 'Tutor',
                'recipient_name': tutor_name or "Unknown Tutor",
                'subject': subject_tutor,
                'body': message_tutor
            })

    # --- Logic for POST request (Send Emails) ---
    if request.method == 'POST':
        send_count = 0
        try:
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
                reason = row['Reason']
                potential_times = row['Potential Times']

                student = Student(student_name, student_email, student_grade, None, subject, info, None, True, None)
                tutor = Tutor(tutor_name, tutor_email, tutor_grade, None, subject, None, True)
                # Note: Matching logic here might be simplified; adapt if needed
                tutor.matched_students = [student]
                student.matched_tutors = [tutor]

                if row['Status'] == 'Matched':
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
                
                if row['Status'] == 'Not Matched':       
                    subject_student = (f'Peer Tutoring Arrangement')
                    student.email = "hliao38@geffenacademy.ucla.edu"
                    if not potential_times:
                        message_student = (f'Dear {student.name}, \n\nUnfortunately, we have not been able to match you with a tutor because {reason}. \n\nRegards, \nGeffen Peer Tutoring Team')
                    else:
                        message_student = (f'Dear {student.name}, \n\nUnfortunately, we have not been able to match you with a tutor because {reason}. \n\nHere are possible time slots you could consider: {not_matched_students[student][1]}\n\nRegards, \nGeffen Peer Tutoring Team')
                    auto_email(student, subject_student, message_student)

            # Save the updated DataFrame back to the CSV file
            df.to_csv(saved_schedule_path, index=False)
            flash(f'Successfully sent {send_count} emails!', 'success')
            # Redirect to GET to avoid re-posting on refresh and show updated previews (which should now be empty)
            return redirect(url_for('email'))

        except Exception as e:
             flash(f'An error occurred during email sending: {e}', 'danger')
             # Re-render the page but show the previews generated before the error
             return render_template('email.html', email_count=email_count, previews=email_previews)


    # Render the template with the generated previews for the GET request
    return render_template('email.html', email_count=email_count, previews=email_previews)

if __name__ == '__main__':
    app.run(debug=True)