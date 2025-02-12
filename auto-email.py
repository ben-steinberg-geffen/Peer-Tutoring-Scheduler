import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart 

'''
def email_tutor(student, matched_tutor):
    message = MIMEMultipart()
    message['From'] = 'peertutoring@geffenacademy.ucla.edu'
    message['To'] = matched_tutor.email

    message['Subject'] = (f'Peer Tutoring with {student.name} on possible dates')
    message['Body'] = (f'Dear {matched_tutor.name}, \n Congratulations! You have succesfully been matched') 
    (f'with {student.name} for peer tutoring in these classes: {student.classes}. {student.name} is available to meet')
    (f'with you on: {student.availability}.')

'''

#TUTOR EMAIL

email = "GeffenPeerTutors@gmail.com"
tutor_email = "cdesai28@geffenacademy.ucla.edu" #replace with tutor's email

subject = ('Geffen Academy Peer Tutoring')
tutor_message = (f'Dear Name,' #replace name with {matched_tutor}
           f'\nYou have been matched with Student for these classes: Class.' #replace Student with {student} and Classes with {matched_classes}
           f'\nStudent is available to meet with you on: Time, Day' #replace Time, Day with {matched_availability} and replace Student with {student}
           '\nRegards,'
           '\n     Geffen Peer Tutoring Team')
tutor_text =  f"Subject: {subject}\n\n{tutor_message}"

#STUDENT EMAIL

student_email = "camrondesai@gmailcom" #replace with student's email
student_message = (f'Dear Name,' #replace name with {student}
           f'\nYou have been matched with Tutor for these classes: Class.' #replace Tutor with {matched_tutor} and Classes with {matched_classes}
           f'\nTutor is available to meet with you on: Time, Day' #replace Time, Day with {matched_availability} and replace Tutor with {matched_tutor}
           '\nRegards,'
           '\n     Geffen Peer Tutoring Team')
student_text =  f"Subject: {subject}\n\n{student_message}"

server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()

server.login(email, "pyke ojyj ixud podl")

server.sendmail(email, tutor_email, tutor_text)

server.sendmail(email, student_email, student_text)

print("Email has been sent to " + tutor_email)
print("Email has been sent to " + student_email)
