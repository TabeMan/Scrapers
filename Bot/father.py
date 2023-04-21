import smtplib
from decouple import config
from weasyprint import HTML
from jinja2 import Template

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


class FatherBot:
    """
    A base class for web scraping bots that crawl websites and generate daily deals reports in PDF format.
    """

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    def __init__(self, caliber, casing, bullet_weight, urls, headers=HEADERS):
        """
        Initializes a new instance of the FatherBot class.

        Args:
            url (str): The URL of the website to crawl.
            headers (dict): A dictionary of HTTP headers to send with each request.
        """
        self.caliber = caliber
        self.casing = casing
        self.bullet_weight = bullet_weight
        self.urls = urls
        self.headers = headers
        self.results = []

    def search(self):
        """
        This method must be implemented by any child class that inherits from FatherBot.
        It should scrape data from a website and populate the self.results list with the results.
        """
        raise NotImplementedError

    def generate_pdf(self, pdf_name):
        """
        Generates a PDF report of the search results.

        Args:
            pdf_name (str): The name of which PDF HTML to open.

        Returns:
            str: The name of the generated PDF file.
        """
        # Open the HTML template file and render the results
        with open(f"{pdf_name}_pdf.html") as file:
            template = Template(file.read())
        html = template.render(results=self.results)

        # Generate PDF from HTML
        pdf_file = "daily_deals.pdf"
        HTML(string=html).write_pdf(pdf_file)
        return pdf_file

    def send_email(self, subject, message, attachment):
        """
        Sends an email message with the daily deals report attached.

        Args:
            subject (str): The subject line of the email.
            message (str): The body of the email message.
            attachment (str): The path to the PDF file to attach to the email.
        """
        recipients = ["tabeman3906@hotmail.com"]
        email = config("GMAIL_EMAIL")
        password = config("GMAIL_PASSWORD")
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = email
        msg["To"] = ", ".join(recipients)
        msg.attach(MIMEText(message))

        # Attach the PDF to the email
        with open(attachment, "rb") as file:
            attachment_data = file.read()
        attachment_part = MIMEApplication(attachment_data, Name="daily_deals.pdf")
        attachment_part["Content-Disposition"] = f"attachment; filename=daily_deals.pdf"
        msg.attach(attachment_part)

        # Send the email
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(email, password)
            smtp.send_message(msg)
            print("Email sent successfully!")

    def run(self):
        """
        Runs the bot to crawl the website, generate the daily deals report, and send it via email.
        """
        try:
            pdf_name = self.search()
            pdf_file = self.generate_pdf(pdf_name)
            self.send_email(
                "Daily Deals Results",
                "We've crawled the web and found the best deals for you! Please see the attached PDF for the results.",
                pdf_file,
            )
        except Exception as e:
            print(f"Error: {e}")
