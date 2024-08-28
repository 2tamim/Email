import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(recipient_email, subject, message):
    # Replace these variables with your email details
    sender_email = 'anson.kindheart@outlook.com'
    password = '123!@#Qaz'
    smtp_server = 'smtp-mail.outlook.com'
    smtp_port = 587  # Update with your SMTP port

    # Create the email message
    email = MIMEMultipart()
    email['From'] = sender_email
    email['To'] = recipient_email
    email['Subject'] = subject

    # Attach the message to the email
    email.attach(MIMEText(message, 'plain'))

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Use TLS encryption

        # Login to your email account
        server.login(sender_email, password)

        # Send the email
        server.sendmail(sender_email, recipient_email, email.as_string())

        print("Email sent successfully")

        # Close the connection
        server.quit()
    except Exception as e:
        print("Email sending failed:", e)
