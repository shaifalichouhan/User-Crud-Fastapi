from app.config import FROM_EMAIL, SENDGRID_API_KEY
import base64
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

def send_invoice_email(to_email: str, subject: str, html_content: str, pdf_path: str = None):
    print("Preparing to send email to:", to_email)
    print("Attachment path received:", pdf_path)

    message = Mail(
        from_email= FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )

    if pdf_path and os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            pdf_data = f.read()
        encoded_file = base64.b64encode(pdf_data).decode()

        attachment = Attachment()
        attachment.file_content = FileContent(encoded_file)
        attachment.file_type = FileType("application/pdf")
        attachment.file_name = FileName(os.path.basename(pdf_path))
        attachment.disposition = Disposition("attachment")

        message.attachment = [
            Attachment(
                file_content=FileContent(
                    encoded_file
                ),
                file_name=FileName("invoice.pdf"),
                file_type=FileType("application/pdfl"),
                disposition=Disposition("attachment"),
            )
        ]

        message.add_attachment(attachment)
        print("PDF attached successfully.")

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print("Email sent:", response.status_code)
    except Exception as e:
        print("Error sending email:", e)
