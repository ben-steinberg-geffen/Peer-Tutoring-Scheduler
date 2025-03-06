import smtplib

#EMAIL ACCOUNT INFORMATION
'''
GeffenPeerTutors@gmail.com
IL0veG3ffen!
'''

def auto_email(recipient, subject, message):
    from_email = 'GeffenPeerTutors@gmail.com'
    # reciever_email = recipient.email
    reciever_email = "ryu@geffenacademy.ucla.edu"

    text =  f"Subject: {subject}\n\n{message}"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(from_email, "pyke ojyj ixud podl")
    server.sendmail(from_email, reciever_email, text)    