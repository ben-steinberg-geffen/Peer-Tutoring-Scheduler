import smtplib
from models import Student, Tutor

def email_Matchedstudent(student, subject, message):

    from_email = 'GeffenPeerTutors@gmail.com'
    reciever_email =  student.email

    #subject = (f'Peer Tutoring with {student.final_tutor.name}')
    #message = (f'Dear {student.name}, \n\nYou have been matched with {student.final_tutor.name} ({student.final_tutor.email}) for peer tutoring in these classes: \n\t{student.courses}. \n\nYou will meet with {student.final_tutor.name} on: \n\t{student.final_time}. \n\nCoordinated directly with {student.final_tutor.name} to decide on a meeting location. \n\n\nThis message has been sent from a send-only e-mail address; please do not reply to this message.')
    text =  f"Subject: {subject}\n\n{message}"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(from_email, "pyke ojyj ixud podl")
    server.sendmail(from_email, reciever_email, text)    

    print("Email has been sent to " + reciever_email)

def email_MatchedTutor(Tutor, subject, message):

    from_email = 'GeffenPeerTutors@gmail.com'
    reciever_email =  Tutor.email

    #subject = (f'Peer Tutoring with {student.final_tutor.name}')
    #message = (f'Dear {student.name}, \n\nYou have been matched with {student.final_tutor.name} ({student.final_tutor.email}) for peer tutoring in these classes: \n\t{student.courses}. \n\nYou will meet with {student.final_tutor.name} on: \n\t{student.final_time}. \n\nCoordinated directly with {student.final_tutor.name} to decide on a meeting location. \n\n\nThis message has been sent from a send-only e-mail address; please do not reply to this message.')
    text =  f"Subject: {subject}\n\n{message}"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(from_email, "pyke ojyj ixud podl")
    server.sendmail(from_email, reciever_email, text)    

    print("Email has been sent to " + reciever_email)

def email_NotMatchedstudent(student, subject, message):

    from_email = 'GeffenPeerTutors@gmail.com'
    reciever_email =  student.email

    #subject = (f'Peer Tutoring with {student.final_tutor.name}')
    #message = (f'Dear {student.name}, \n\nYou have been matched with {student.final_tutor.name} ({student.final_tutor.email}) for peer tutoring in these classes: \n\t{student.courses}. \n\nYou will meet with {student.final_tutor.name} on: \n\t{student.final_time}. \n\nCoordinated directly with {student.final_tutor.name} to decide on a meeting location. \n\n\nThis message has been sent from a send-only e-mail address; please do not reply to this message.')
    text =  f"Subject: {subject}\n\n{message}"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(from_email, "pyke ojyj ixud podl")
    server.sendmail(from_email, reciever_email, text)    

    print("Email has been sent to " + reciever_email)


#------- FOR TESTING
Derek = Student("null","null","null","null","null","null")
MrRioveros = Tutor("null","null","null","null","null","null")



Derek.name = "Derek"
Derek.email = "driover73@geffenacademy.ucla.edu"
Derek.availability = "1pm"
Derek.courses = "Math"
Derek.matched_tutors = [MrRioveros]
Derek.grade = "12"
#Derek.final_tutor = MrRioveros
#Derek.final_time = "1pm"

MrRioveros.name = "Mr. Rioveros"
MrRioveros.email = "driover73@geffenacademy.ucla.edu"
MrRioveros.grade = "12"
MrRioveros.availability = "1pm"
MrRioveros.courses = "Math"
MrRioveros.matched_students = [Derek]
MrRioveros.final_students = {Derek} 

message = (f'Dear {Derek.name}, \n\nYou have been matched with {Derek.final_tutor.name} ({Derek.final_tutor.email}) for peer tutoring in these classes: \n\t{Derek.courses}. \n\nYou will meet with {Derek.final_tutor.name} on: \n\t{Derek.final_time}. \n\nCoordinated directly with {Derek.final_tutor.name} to decide on a meeting location. \n\n\nThis message has been sent from a send-only e-mail address; please do not reply to this message.')
subject = (f'Peer Tutoring with {Derek.final_tutor.name}')

email_Matchedstudent(Derek, subject, message)