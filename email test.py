
import smtplib

# creates SMTP session
s = smtplib.SMTP('smtp.gmail.com', 587)
# start TLS for security
s.starttls()
# Authentication
s.login("comsciii77@gmail.com", "testpassword123")
# message to be sent
message = "Message_you_need_to_send"
# sending the mail
s.sendmail("comsciii77@gmail.com", "erobins95@geffenacademy.ucla.edu", message)
# terminating the session
s.quit()
