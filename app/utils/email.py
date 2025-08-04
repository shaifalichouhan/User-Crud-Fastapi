import os
import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from app.config import FROM_EMAIL, SENDGRID_API_KEY

def send_invoice_email(to_email: str, subject: str, html_content: str, pdf_path: str = None):
    print("Preparing to send email to:", to_email)
    print("Attachment path received:", pdf_path)

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )

    if pdf_path and os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            data = f.read()
            encoded = base64.b64encode(data).decode()
            attachment = Attachment(
                FileContent(encoded),
                FileName("invoice.pdf"),
                FileType("application/pdf"),
                Disposition("attachment")
            )
            message.attachment = attachment
    else:
        print("Attachment not found or not provided:", pdf_path)

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print("Email sent:", response.status_code)
    except Exception as e:
        print("SendGrid error:", e)
