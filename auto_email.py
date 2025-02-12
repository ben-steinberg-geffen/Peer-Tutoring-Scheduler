import smtplib
from main import Student, Tutor

def email_student(Student, Tutor):
    #message['From'] = 'peertutoring@geffenacademy.ucla.edu'
    #message['To'] = student.email

    #message['Subject'] = (f'Peer Tutoring with {matched_tutor.name}')
        
    email = "GeffenPeerTutors@gmail.com"
    reciever_email = "driover73@geffenacademy.ucla.edu"

    subject = (f'Peer Tutoring with {Tutor.name}')
    #message = (f'Dear {student.name}, \n\nYou have been matched with {matched_tutor.name} ({matched_tutor.email}) for peer tutoring in these classes: \n\t{student.classes}. \n\nYou will meet with {matched_tutor.name} on: \n\t{student.final_time}. \n\nCoordinated directly with {matched_tutor.name} to decide on a meeting location. \n\n\nThis message has been sent from a send-only e-mail address; please do not reply to this message.')
    message = ("Hello!")
    text =  f"Subject: {subject}\n\n{message}"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(email, "pyke ojyj ixud podl")
    server.sendmail(email, reciever_email, text)    

    print("Email has been sent to " + reciever_email)

def checkavailaibility(student, tutor):
    intersection = []
    for student.availability in student:
        for tutor.availability in tutor:
            if student.availability == tutor.availability:
                intersection.append(student.availability, tutor.availaibility)
    return intersection

Ethan = Student()
John = Tutor()



Ethan.name = "Ethan"
Ethan.email = "ethankrobinson@gmail.com"
Ethan.availability = "1:00pm"
Ethan.courses = "Math"
Ethan.matched_tutors = [John]
Ethan.grade = "11"
Ethan.tutor_index = 0 
Ethan.time_index = 0
Ethan.final_tutor = None
Ethan.final_time = None
Student 

John.name = "John"
John.email = "GeffenPeerTutors@gmail.com"
John.grade = "11"
John.availability = "1pm"
John.courses = "Math"
John.matched_students = [Ethan]
John.final_students = {} 

email_student(Ethan, John)