import whois
import datetime
import csv
import smtplib
import logging
import os

# Configure logging
logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def get_domain_info(domain):
    try:
        w = whois.whois(domain)
        return w
    except whois.parser.PywhoisError as e:
        logging.error(f"Error retrieving WHOIS info for {domain}: {str(e)}")
        return None

def extract_details(domain_info):
    if domain_info is None:
        return None
    else:
        name = domain_info.name
        domain_name = domain_info.domain_name[0]
        email = domain_info.emails[0]
        phone = domain_info.phone
        return name, domain_name, email, phone

def is_registered_today(domain_info):
    if domain_info is None:
        return False
    else:
        creation_date = domain_info.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        return creation_date.date() == datetime.date.today()

def process_domain(domain, writer):
    domain_info = get_domain_info(domain)
    if is_registered_today(domain_info):
        details = extract_details(domain_info)
        if details is not None:
            name, domain_name, email, phone = details
            registration_date = datetime.datetime.now()
            writer.writerow([name, domain_name, email, phone, registration_date])

def send_email(subject, body, sender_email, receiver_email, smtp_server, smtp_port, smtp_username, smtp_password):
    message = f"Subject: {subject}\n\n{body}"
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, receiver_email, message)
    except Exception as e:
        logging.error(f"Error sending email: {str(e)}")

# Example usage
domains = ["google.com"]  # Add your domain names here

# Set up SMTP email configuration
sender_email = "singhsaurabh945198@gmail.com"
receiver_email = "singhsaurabh9451985554@gmail.com"
smtp_server = "smtp.googlemail.com"
smtp_port = 587
smtp_username = os.environ.get('EMAIL_USER')
smtp_password = os.environ.get('EMAIL_USER')

# Set up email subject and body
email_subject = "Domain Registration Details"
email_body = "Here are the extracted details of newly registered domains:\n\n"

with open('registrations.csv', 'a', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for domain in domains:
        process_domain(domain, writer)
        email_body += f"Domain: {domain}\n" 


# Send email
send_email(email_subject, email_body, sender_email, receiver_email, 
           smtp_server, smtp_port, smtp_username, smtp_password)
