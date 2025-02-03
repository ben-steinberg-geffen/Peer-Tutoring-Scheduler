import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart 

def email_student(student, matched_tutor):
    message = MIMEMultipart()
    message['From'] = 'peertutoring@geffenacademy.ucla.edu'
    message['To'] = student.email

    message['Subject'] = (f'Peer Tutoring with {matched_tutor.name} on possible dates')
    message['Body'] = (f'Dear {student.name}, \n Congratulations! You have succesfully been matched') 
    (f'with {matched_tutor.name} for peer tutoring in these classes: {student.classes}. {matched_tutor.name} is available to meet')
    (f'with you on: {student.availability}.')

def email_tutor(matched_student, tutor):
    message = MIMEMultipart()
