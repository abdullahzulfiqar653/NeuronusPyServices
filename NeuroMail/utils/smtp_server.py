import os
import smtplib
import requests
from django.conf import settings
from urllib.parse import urlparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

SMTP_SERVER = settings.MAIL_SERVER
SMTP_PORT = 587  # Use 587 for TLS, 465 for SSL


def send_email(
    subject,
    body,
    from_email,
    password,
    recipients,
    attachments=[],
):
    """
    Send an email with the given subject, body, and attachments.
    """

    msg = MIMEMultipart(
        "alternative"
    )  # Set alternative to send both plain text and HTML
    msg["From"] = from_email
    msg["Subject"] = subject

    def get_emails(filter_type):
        return [
            recipient["email"]
            for recipient in recipients
            if recipient["recipient_type"] == filter_type
        ]

    # Set the 'To', 'Cc', and handle 'Bcc' separately
    to_emails = get_emails("to")
    cc_emails = get_emails("cc")
    bcc_emails = get_emails("bcc")

    all_emails = to_emails + cc_emails + bcc_emails

    msg["To"] = ", ".join(to_emails)
    msg["Cc"] = ", ".join(cc_emails)

    # Attach plain text version (fallback)
    plain_body = body.strip()  # In case you want to handle plain text
    msg.attach(MIMEText(plain_body, "plain"))

    
    msg.attach(MIMEText(body, "html"))

    # Attach files if any
    if attachments:
        for url in attachments:
            try:
                # Download the file from the presigned URL
                response = requests.get(url)
                if response.status_code == 200:
                    file_content = response.content
                    filename = os.path.basename(
                        urlparse(url).path
                    )  # Extract filename from the URL

                    # Attach the file
                    part = MIMEApplication(file_content, Name=filename)
                    part["Content-Disposition"] = f'attachment; filename="{filename}"'
                    msg.attach(part)
                else:
                    print(
                        f"Failed to download file from {url}, status code {response.status_code}"
                    )
            except Exception as e:
                print(f"Failed to attach file from URL {url}: {e}")

    try:
        # Connect to the server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Upgrade the connection to secure
        server.login(from_email, password)

        # Send the email to all recipients, including Bcc
        server.sendmail(from_email, all_emails, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
    finally:
        server.quit()