#This is used to test if the email is working: Problems may come from app password in google account


import smtplib


email = "geffenpeertutors@gmail.com"
reciever_email = ["driover73@geffenacademy.ucla.edu"]

subject = (f'TEST')
message = (f'Sent By A Bot')

text =  f"Subject: {subject}\n\n{message}"

server = smtplib.SMTP("smtp.gmail.com", 587) #587
server.ehlo()
server.starttls()
server.ehlo()

server.login(email, "pykeojyjixudpodl") # 1: pyke ojyj ixud podl

server.sendmail(email, reciever_email, text)
server.quit()

print("Email has been sent to " + reciever_email)