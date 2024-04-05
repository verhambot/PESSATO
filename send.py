import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.mime.base import MIMEBase
from dotenv import load_dotenv
import os
from twilio.rest import Client
from fpdf import FPDF

load_dotenv()

account_sid = os.getenv("ACC_SID")
auth_token = os.getenv("AUTH_TOKEN")
client = Client(account_sid, auth_token)


def _email(email_send, subject, body, att=False):
    password = os.getenv("EMAIL_PASS")
    email_user = "<EMAIL>"
    email_password = password
    msg = MIMEMultipart()
    msg["From"] = email_user
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    if att:
        attachment = open("static/assets/pdf/output.pdf", "rb")
        part = MIMEBase("application", "octet-stream")
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment; filename=order_receipt.pdf")
        msg.attach(part)
    text = msg.as_string()
    server = smtplib.SMTP("smtp.gmail.com:587")
    server.ehlo("localhost")
    server.starttls()
    server.ehlo("localhost")
    server.login(email_user, email_password)
    server.sendmail(email_user, email_send, text)
    server.quit()
    print("email sent")


def _msg(ph, otp):
    b = f"Your PESSATO OTP for login is {otp}"
    message = client.messages.create(from_="+12164382762", body=b, to=ph)


li = []


def getter(lii):
    global li
    li = lii


class PDF(FPDF):
    def header(self):
        pdf.set_font("helvetica", "B", 24)
        pdf.cell(0, 10, "PESSATO", align="C", border=False)
        self.ln(50)
        pdf.set_font("helvetica", "", 18)
        pdf.cell(0, 10, f"orderno:{li[0]}", align="L", border=False)
        self.ln(10)
        pdf.set_font("helvetica", "", 24)
        pdf.cell(0, 10, "-" * 70, align="C", border=False)
        pdf.set_font("helvetica", "", 24)
        self.ln(10)
        pdf.cell(0, 10, "RECEIPT", align="C", border=False)
        self.ln(10)
        pdf.cell(0, 10, "-" * 70, align="C", border=False)


pdf = PDF("P", "mm", "A4")


def _createPDF():
    pdf.add_page()
    pdf.set_font("helvetica", "B", 15)
    pdf.ln(10)
    pdf.cell(90, 10, f"Description", align="L", border=False)
    pdf.cell(50, 10, f"Quantity", align="L", border=False)
    pdf.cell(50, 10, f"Price", align="L", border=False)
    pdf.ln(10)
    pdf.set_font("helvetica", "", 15)
    sum = 0.0
    for i in range(1, len(li)):
        sum += float(li[i][2] * li[i][1])
        pdf.cell(90, 10, f"{li[i][0]}", align="L", border=False)
        pdf.cell(50, 10, f"{li[i][1]}", align="L", border=False)
        pdf.cell(50, 10, f"Rs.{li[i][2]*li[i][1]}", align="L", border=False)
        pdf.ln(10)
    sum = round(sum, 2)
    pdf.set_font("helvetica", "B", 24)
    pdf.cell(0, 10, "-" * 70, align="C", border=False)
    pdf.ln(10)
    pdf.set_font("helvetica", "", 20)
    pdf.cell(90, 10, f"Total", align="L", border=False)
    pdf.cell(50, 10, f"", align="L", border=False)
    pdf.cell(50, 10, f"Rs.{sum}", align="L", border=False)
    pdf.ln(10)
    gst = round(0.18 * sum, 2)
    pdf.cell(90, 10, f"TAX", align="L", border=False)
    pdf.cell(50, 10, f"", align="L", border=False)
    pdf.cell(50, 10, f"Rs.{gst}", align="L", border=False)
    pdf.ln(10)
    pf = 4
    pdf.cell(90, 10, f"Restaurant Charge", align="L", border=False)
    pdf.cell(50, 10, f"", align="L", border=False)
    pdf.cell(50, 10, f"{pf}", align="L", border=False)
    pdf.ln(10)
    pdf.cell(90, 10, f"Grand Total", align="L", border=False)
    pdf.cell(50, 10, f"", align="L", border=False)
    pdf.cell(50, 10, f"Rs.{round(gst+sum+pf,2)}", align="L", border=False)
    output_path = "static/assets/pdf/output.pdf"
    pdf.output(name=output_path, dest="F")
