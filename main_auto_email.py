import smtplib
from models import Student, Tutor

#EMAIL ACCOUNT INFORMATION

subject = "Geffen Peer Tutoring"


def email_matched_student(student, subject, message):

    from_email = 'peertutoring2@geffenacademy.ucla.edu'
    reciever_email = [student.email] #ADD MS MILLY EMAIL

    studentMessage = (f'Dear {student},'
                  f'\nYou have been matched with {student.final_tutor.name} for Peer Tutoring in the following class: {",".join(student.courses)}.'
                  f'\n{student.final_tutor.name} is available to meet you at {student.final_time}. '
                  f'\nPlease coordinate with {student.final_tutor.name} to set up a meeting spot.'
                  '\nRegards,'
                  '\n     Geffen Peer Tutoring Team'
                  '\n\nTHIS IS AN AUTOMATED EMAIL, DO NOT REPLY TO THIS MESSAGE.')
    #subject = (f'Peer Tutoring with {student.final_tutor.name}')
    #message = (f'Dear {student.name}, \n\nYou have been matched with {student.final_tutor.name} ({student.final_tutor.email}) for peer tutoring in these classes: \n\t{student.courses}. \n\nYou will meet with {student.final_tutor.name} on: \n\t{student.final_time}. \n\nCoordinated directly with {student.final_tutor.name} to decide on a meeting location. \n\n\nThis message has been sent from a send-only e-mail address; please do not reply to this message.')
    text =  f"Subject: {subject}\n\n{message}"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(from_email, "auam cwoo skkj epqv")
    server.sendmail(from_email, reciever_email, text)    

    print("Email has been sent to " + reciever_email)

def email_matched_tutor(Tutor, subject, message):

    from_email = 'peertutoring2@geffenacademy.ucla.edu'
    reciever_email =  [Tutor.email] #ADD MS MILLY EMAIL

    text =  f"Subject: {subject}\n\n{message}"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(from_email, "auam cwoo skkj epqv")
    server.sendmail(from_email, reciever_email, text)    

    print("Email has been sent to " + reciever_email)

def email_not_matched_student(student, subject, message):

    from_email = 'peertutoring2@geffenacademy.ucla.edu'
    reciever_email =  [student.email] #ADD MS MILLY EMAIL

    text =  f"Subject: {subject}\n\n{message}"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(from_email, "auam cwoo skkj epqv")
    server.sendmail(from_email, reciever_email, text)    

    print("Email has been sent to " + reciever_email)


#------- FOR TESTING
'''

if __name__ == "__main__":
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

    message = (f'Sent by a bot')
    subject = (f'Python Email Test')

    email_Matchedstudent(Derek, subject, message)
    email_MatchedTutor(Derek, subject, message)
    email_NotMatchedstudent(Derek, subject, message)

'''