import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from .models import TaskChunk
from django.http import HttpResponse
from django_q.tasks import async_task


def send_target_emails(args):
    chunk = TaskChunk.objects.get(pk=args)


    # Read the HTML file content from the modelfile field
    email_html = chunk.task.template.read().decode('utf-8')  # Assuming modelfile stores HTML content

    # Parse HTML content using BeautifulSoup
    soup = BeautifulSoup(email_html, 'html.parser')

    # for target in task.target_list.all():
    email = chunk.target.email
    name = chunk.target.name
    lastname = chunk.target.lastname
    phone = chunk.target.phone


    # Find specific tags in the HTML content and replace their content with database info
    target_user_email_tag = soup.find('span', {'class': 'target_user_email'})

    target_user_lastname_tag = soup.find('span', {'class': 'target_user_lastname'})

    target_user_phone_tag = soup.find('span', {'class': 'target_user_phone'})

    target_user_name_tag = soup.find('span', {'class': 'target_user_name'})


    if target_user_name_tag:
        target_user_name_tag.string = name  # Replace with the fetched email

    elif target_user_email_tag:
        target_user_email_tag.string = email  # Replace with the fetched email

    elif target_user_lastname_tag:
        target_user_lastname_tag.string = lastname  # Replace with the fetched email

    elif target_user_phone_tag:
        target_user_phone_tag.string = phone  # Replace with the fetched email


    # Get the modified HTML content
    customized_html = str(soup)

    # Connect to SMTP server and send email
    smtp_server = chunk.task.my_email.host_server  # Replace with your SMTP server
    smtp_port = chunk.task.my_email.port_server  # Replace with your SMTP port
    smtp_username = chunk.task.my_email.email  # Replace with your SMTP username
    smtp_password = chunk.task.my_email.password  # Replace with your SMTP password

    # Create MIMEMultipart object
    message = MIMEMultipart()
    message['From'] = chunk.task.my_email.email  # Replace with your email
    message['To'] = str(email)  # Replace with recipient email (converted to string)
    message['Subject'] = 'Subject of Your Email'

    # Attach the HTML content to the email
    message.attach(MIMEText(customized_html, 'html'))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(message)

    return HttpResponse('Email sent successfully')


def check_my_email(args):
    chunk = TaskChunk.objects.get(pk=args)

    # Connect to SMTP server and send email
    smtp_server = chunk.task.my_email.host_server
    smtp_port = chunk.task.my_email.port_server
    smtp_username = chunk.task.my_email.email
    smtp_password = chunk.task.my_email.password

    # Create MIMEMultipart object
    message = MIMEMultipart()
    message['From'] = chunk.task.my_email.email
    message['To'] = chunk.task.my_email.email
    message['Subject'] = 'Who am i?'

    text_content = "This is a test email."

    # Create the message
    message = MIMEText(text_content)

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(message)

    return HttpResponse('Email sent successfully')
