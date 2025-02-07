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

email = "GeffenPeerTutors@gmail.com"
reciever_email = "driover73@geffenacademy.ucla.edu"

subject = input("SUBJECT: ")
message = input("MESSAGE: ")

text =  f"Subject: {subject}\n\n{message}"

server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()

server.login(email, "pyke ojyj ixud podl")

server.sendmail(email, reciever_email, text)

print("Email has been sent to " + reciever_email)