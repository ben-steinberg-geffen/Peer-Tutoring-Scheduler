import smtplib

#EMAIL ACCOUNT INFORMATION
'''
peertutoring2@geffenacademy.ucla.edu
OREOSAREBADFORYOU35
'''

def auto_email(recipient, subject, message):
    from_email = 'peertutoring2@geffenacademy.ucla.edu'
    recipient_email = 'driover73@geffenacademy.ucla.edu' #recipient.email

    text = f"Subject: {subject}\n\n{message}"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(from_email, "auam cwoo skkj epqv") #Passkey password
    server.sendmail(from_email, recipient_email, text)    