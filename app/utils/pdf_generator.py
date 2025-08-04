from xhtml2pdf import pisa
import os

def generate_invoice_pdf(session_id: str, amount: float) -> str:
    try:
        html = f"""
        <html>
            <body>
                <h2>Invoice</h2>
                <p><strong>Session ID:</strong> {session_id}</p>
                <p><strong>Amount Paid:</strong> {amount} USD</p>
            </body>
        </html>
        """

        invoices_dir = "invoices"
        if not os.path.exists(invoices_dir):
            os.makedirs(invoices_dir)

        file_path = os.path.join(invoices_dir, f"invoice_{session_id}.pdf")
        with open(file_path, "wb") as f:
            pisa_status = pisa.CreatePDF(html, dest=f)

        if pisa_status.err:
            print("Failed to generate PDF.")
        else:
            print("PDF generated at:", os.path.abspath(file_path))

        return os.path.abspath(file_path)

    except Exception as e:
        print("Error in PDF generation:", e)
        return ""
