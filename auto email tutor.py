import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart 
student = []
matched_tutor = []

def email_tutor(student, matched_tutor):
    message = MIMEMultipart()
    message['From'] = 'peertutoring@geffenacademy.ucla.edu'
    message['To'] = matched_tutor.email

    message['Subject'] = f'Peer Tutoring with {student.name} on possible dates'
    message['Body'] = f'Dear {matched_tutor.name}, \n Congratulations! You have succesfully been matched 
    with {student.name} for peer tutoring in these classes: {student.classes}. {student.name} is available to meet
    with you on: {student.availability}.'
    
email = email_tutor(student, matched_tutor)
print(email)

# def email_tutor(matched_student, tutor):
#     message = MIMEMultipart()