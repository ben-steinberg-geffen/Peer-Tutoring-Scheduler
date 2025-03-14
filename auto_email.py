import smtplib

#EMAIL ACCOUNT INFORMATION
'''
peertutoring2@geffenacademy.ucla.edu
OREOSAREBADFORYOU35
'''

def auto_email(recipient, subject, message):
    from_email = 'peertutoring2@geffenacademy.ucla.edu'
    recipient_email = recipient.email

    text = f"Subject: {subject}\n\n{message}"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(from_email, "OREOSAREBADFORYOU35")
    server.sendmail(from_email, recipient_email, text)    