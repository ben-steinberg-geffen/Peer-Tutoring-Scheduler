import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart 

def email_student(student, matched_tutor):
    message = MIMEMultipart()
    message['From'] = 'peertutoring@geffenacademy.ucla.edu'
    message['To'] = student.email

    message['Subject'] = (f'Peer Tutoring with {matched_tutor.name}')
    message['Body'] = (f'Dear {student.name}, \n\nYou have been matched with {matched_tutor.name} ({matched_tutor.email}) for peer tutoring in these classes: \n\t{student.classes}. \n\nYou will meet with {matched_tutor.name} on: \n\t{student.final_time}. \n\nCoordinated directly with {matched_tutor.name} to decide on a meeting location. \n\n\nThis message has been sent from a send-only e-mail address; please do not reply to this message.')

def email_tutor(matched_student, tutor):
    message = MIMEMultipart()
    message['From'] = 'peertutoring@geffenacademy.ucla.edu'
    message['To'] = matched_student.email

    message['Subject'] = (f'Peer Tutoring with {matched_student.name}')
    message['Body'] = (f'Dear {tutor.name}, \n\nYou have been matched with {matched_student.name} ({matched_student.email}) for peer tutoring in these classes: \n\t{matched_student.classes}. \n\nYou will meet with {matched_student.name} on: {matched_student.final_time}. \n\nCoordinate directly with {matched_student.name} to decide on a meeting location. \n\n\nThis message has been sent from a send-only e-mail address; please do not reply to this message.')


def checkavailaibility(student, tutor):
    intersection = []
    for student.availability in student:
        for tutor.availability in tutor:
            if student.availability == tutor.availability:
                intersection.append(student.availability, tutor.availaibility)
    return intersection
