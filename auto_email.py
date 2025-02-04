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
    message['From'] = 'peertutoring@geffenacademy.ucla.edu'
    message['To'] = matched_student.email

    message['Subject'] = f'Peer Tutoring with {matched_student.name} on possible dates'
    message['Body'] = f'Dear {tutor.name}, \n Congratulations! You have succesfully been matched with {matched_student.name} for peer tutoring in these classes: {matched_student.classes}. {matched_student.name} is available to meet with you on: {matched_student.availability}.'

def checkavailaibility(student, tutor):
    intersection = []
    for student.availability in student:
        for tutor.availability in tutor:
            if student.availability == tutor.availability:
                intersection.append(student.availability, tutor.availaibility)
    return intersection
