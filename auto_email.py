import smtplib

#EMAIL ACCOUNT INFORMATION
'''
Email: peertutoring2@geffenacademy.ucla.edu
Password: OREOSAREBADFORYOU35
App Password: 
'''
# aiwy sost pake vabx

def auto_email(recipient, subject, message):
    # from_email = 'peertutoring2@geffenacademy.ucla.edu'
    from_email = "geffentutoring@gmail.com"
    recipient_email = "hliao38@geffenacademy.ucla.edu"

    text = f"Subject: {subject}\n\n{message}"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(from_email, "aiwy sost pake vabx")
    server.sendmail(from_email, recipient_email, text)