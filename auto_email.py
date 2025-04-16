import smtplib

#EMAIL ACCOUNT INFORMATION
'''
Email: peertutoring2@geffenacademy.ucla.edu
Password: OREOSAREBADFORYOU35
App Password: auam cwoo skkj epqv
'''

def auto_email(recipient, subject, message):
    from_email = 'peertutoring2@geffenacademy.ucla.edu'
<<<<<<< HEAD
    recipient_email = 'driover73@geffenacademy.ucla.edu' #recipient.email
=======
    recipient_email = "hliao38@geffenacademy.ucla.edu"
>>>>>>> 30883ae0fec2038a3b25546748444aaf5898ecd3

    text = f"Subject: {subject}\n\n{message}"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
<<<<<<< HEAD
    server.login(from_email, "auam cwoo skkj epqv") #Passkey password
    server.sendmail(from_email, recipient_email, text)    
=======
    server.login(from_email, "auam cwoo skkj epqv")
    server.sendmail(from_email, recipient_email, text)
>>>>>>> 30883ae0fec2038a3b25546748444aaf5898ecd3
