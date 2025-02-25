import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart 
import csv

class finalmatches:
    def __init__ (self, tutorname, tutoremail, studentname, studentemail, courses, finaltimes):
        self.tutorname = tutorname
        self.tutoremail = tutoremail

        self.studentname = studentname
        self.studentemail = studentemail

        self.courses = courses
        self.finaltimes = finaltimes


sample_finalmatch = finalmatches(
    tutorname="John",
    tutoremail="ethankrobinson@gmail.com",
    studentname="Mike",
    studentemail="mike@gmail.com",
    courses="Math",
    finaltimes="3:10pm"
)

matches_list = []

with open('tutoring_schedule.csv', mode='r', newline='') as file:
    csvFile = csv.reader(file)
    skipheader = next(csvFile) 

    for line in csvFile:
        if len(line) < 6: 
            continue

        tutorname = line[2]
        tutoremail = line[3].strip()
        studentname = line[0]
        studentemail = line[1].strip()
        courses = line[4]
        finaltimes = line[5]

        match = finalmatches(tutorname, tutoremail, studentname, studentemail, courses, finaltimes)
        matches_list.append(match)

#print(f"{match.studentname} is matched with {match.tutorname} for {match.courses} during {match.finaltimes}")
    

def email_tutor(emailmatch):
    email = "GeffenPeerTutors@gmail.com"

    reciever_email = emailmatch.tutoremail

    subject = (f'Peer Tutoring with {emailmatch.studentname} on possible dates')

    message = (f'Dear {emailmatch.tutorname}, \nCongratulations! You have succesfully been matched with {emailmatch.studentname} for peer tutoring in these classes: {emailmatch.courses}. {emailmatch.studentname} is available to meet with you on: {emailmatch.finaltimes}.')

    text =  f"Subject: {subject}\n\n{message}"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(email, "pyke ojyj ixud podl")
    server.sendmail(email, reciever_email, text)

    print("Email has been sent to " + reciever_email)





def email_student(emailmatch):
    email = "GeffenPeerTutors@gmail.com"
    
    reciever_email = emailmatch.studentemail

    subject = (f'Peer Tutoring with {emailmatch.tutorname} on possible dates')

    message = (f'Dear {emailmatch.studentname}, \nCongratulations! You have succesfully been matched with {emailmatch.tutorname} for peer tutoring in these classes: {emailmatch.courses}. {emailmatch.tutorname} is available to meet with you on: {emailmatch.finaltimes}.')

    text =  f"Subject: {subject}\n\n{message}"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(email, "IL0veG3ffen!")
    server.sendmail(email, reciever_email, text)
    
    print("Email has been sent to " + reciever_email)


def email_all():
    for match in matches_list:
        email_student(match)
        email_tutor(match)


