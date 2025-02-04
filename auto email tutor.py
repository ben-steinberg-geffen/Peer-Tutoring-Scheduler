import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart 

def email_tutor(student, matched_tutor):
    message = MIMEMultipart()
    message['From'] = 'peertutoring@geffenacademy.ucla.edu'
    message['To'] = matched_tutor.email

    message['Subject'] = (f'Peer Tutoring with {student.name} on possible dates')
    message['Body'] = (f'Dear {matched_tutor.name}, \n Congratulations! You have succesfully been matched') 
    (f'with {student.name} for peer tutoring in these classes: {student.classes}. {student.name} is available to meet')
    (f'with you on: {student.availability}.')

# def email_tutor(matched_student, tutor):
#     message = MIMEMultipart()
#asdufadsfs