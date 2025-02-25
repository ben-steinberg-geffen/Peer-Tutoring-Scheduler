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

#print(sample_finalmatch.studentname)


#with open('tutoring_schedule.csv', mode ='r')as file:
 #   csvFile = csv.reader(file)
  #  for lines in csvFile:
   #     print(lines)

    


def email_tutor(emailmatch):
    email = "GeffenPeerTutors@gmail.com"
#reciever_email = "driover73@geffenacademy.ucla.edu"
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
    
#reciever_email = "driover73@geffenacademy.ucla.edu"
    reciever_email = emailmatch.studentemail

    subject = (f'Peer Tutoring with {emailmatch.tutorname} on possible dates')

    message = (f'Dear {emailmatch.studentname}, \nCongratulations! You have succesfully been matched with {emailmatch.tutorname} for peer tutoring in these classes: {emailmatch.courses}. {emailmatch.tutorname} is available to meet with you on: {emailmatch.finaltimes}.')

    text =  f"Subject: {subject}\n\n{message}"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(email, "IL0veG3ffen!")
    server.sendmail(email, reciever_email, text)


    #IL0veG3ffen!
    #
    
    print("Email has been sent to " + reciever_email)

#email_tutor(sample_finalmatch)
#appendix interframe

email_tutor(sample_finalmatch)

#email_tutor(sample_finalmatch)
