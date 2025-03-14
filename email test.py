#This is used to test if the email is working: Problems may come from app password in google account


import smtplib


email = "peertutoring2@geffenacademy.ucla.edu" #"geffenpeertutors@gmail.com"
reciever_email = ["deangelopro1025@gmail.com", "driover73@geffenacademy.ucla.edu"] # "driover73@geffenacademy.ucla.edu"

subject = (f'Peer Tutoring Scheduler')
message = (f'Hi Derek,\n\nYou have been matched with Derek Rioveros for Peer Tutoring for Calculus. Please reachout to him at driover73@geffenacademy.ucla.edu.\n\nBest,\nDerek Rioveros')

text =  f"Subject: {subject}\n\n{message}"

server = smtplib.SMTP("smtp.gmail.com", 587) #587
server.ehlo()
server.starttls()
server.ehlo()

server.login(email, "auam cwoo skkj epqv") # OLD PASS WORD (For old Email): pyke ojyj ixud podl

server.sendmail(email, reciever_email, text)
server.quit()

print("Email has been sent to ", reciever_email)