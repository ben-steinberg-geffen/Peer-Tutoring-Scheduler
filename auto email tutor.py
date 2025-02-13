import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart 

class finalmatches:
    def __init__(self, tutorname, tutoremail, courses, finaltimes, studentname, studentemail):
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


'''

1. a is a long line of crap A = readfile!
2. a line of crap seperated into linesA = splitlines(A)
3. Amy, Adams, "BobBuilder"
4. for i in A:
    j = i.split(",")
        ("AmyAtoms", "inequal.com",)

    readline
"blah, blah: ..."
"blah, blah2f..."
we need to recognize the pieces of data, studentdata.csv"

'''

#Student Name,Student Email,Tutor Name,Tutor Email,Course,Time

def email_tutor(finalmatches):
    email = "GeffenPeerTutors@gmail.com"
#reciever_email = "driover73@geffenacademy.ucla.edu"
    reciever_email = sample_finalmatch.tutoremail

    subject = (f'Peer Tutoring with {sample_finalmatch.studentname} on possible dates')

    message = (f'Dear {sample_finalmatch.tutorname}, \n Congratulations! You have succesfully been matched with {sample_finalmatch.studentname} for peer tutoring in these classes: {sample_finalmatch.courses}. {sample_finalmatch.studentname} is available to meet with you on: {sample_finalmatch.finaltimes}.')

    text =  f"Subject: {subject}\n\n{message}"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(email, "pyke ojyj ixud podl")
    server.sendmail(email, reciever_email, text)

    print("Email has been sent to " + reciever_email)


def email_student(finalmatches):
    email = "GeffenPeerTutors@gmail.com"
#reciever_email = "driover73@geffenacademy.ucla.edu"
    reciever_email = sample_finalmatch.studentemail

    subject = (f'Peer Tutoring with {sample_finalmatch.tutorname} on possible dates')

    message = (f'Dear {sample_finalmatch.studentname}, \n Congratulations! You have succesfully been matched with {sample_finalmatch.tutorname} for peer tutoring in these classes: {sample_finalmatch.courses}. {sample_finalmatch.tutorname} is available to meet with you on: {sample_finalmatch.finaltimes}.')

    text =  f"Subject: {subject}\n\n{message}"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(email, "pyke ojyj ixud podl")
    server.sendmail(email, reciever_email, text)
    
    print("Email has been sent to " + reciever_email)

#email_tutor(sample_finalmatch)
#appendix interframe


email_tutor(sample_finalmatch)