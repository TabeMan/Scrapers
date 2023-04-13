import requests
import smtplib
import os
from decouple import config
from weasyprint import HTML
from jinja2 import Template
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import logging

# Set up logging
logging.basicConfig(
    filename="bot.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

NEWEGG_URL = "https://www.newegg.com/todays-deals?cm_sp=Head_Navigation-_-Under_Search_Bar-_-Today%27s+Best+Deals&icid=720202"
BEST_BUY_URL = "https://www.bestbuy.com/site/electronics/top-deals/pcmcat1563299784494.c?id=pcmcat1563299784494"


def search_newegg(url):
    page = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(page.content, "html.parser")
    final = []

    inner = soup.find("div", {"class": "item-cells-wrap tile-cells five-cells"})

    for row in inner.find_all("div", {"class": "item-cell"}):
        result = {}
        result["title"] = row.find("a", {"class": "item-title"}).text.strip()
        result["link"] = row.find("a", {"class": "item-title"}).get("href")
        result["price_was"] = row.find("li", {"class": "price-was"}).text.strip()
        result["price_current"] = (
            row.find("li", {"class": "price-current"})
            .text.strip()
            .split("–")[0]
            .replace("\xa0", "")
        )
        result["price_savings"] = row.find("li", {"class": "price-save"}).text.strip()

        final.append(result)
    return final


def generate_pdf(results):
    # Load the HTML template
    with open("pdf.html") as file:
        template = Template(file.read())

    # Render the template with the results
    html = template.render(results=results)

    # Generate the PDF
    pdf_file = "daily_deals.pdf"
    HTML(string=html).write_pdf(pdf_file)

    return pdf_file


def send_email(subject, message, attachment):
    recipients = ["tabeman3906@hotmail.com"]
    email = config("GMAIL_EMAIL")
    password = config("GMAIL_PASSWORD")
    # Create the email message
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = email
    msg["To"] = ", ".join(recipients)

    # Attach the message body as plain text
    msg.attach(MIMEText(message))

    # Attach the PDF file to the email
    with open(attachment, "rb") as file:
        attachment_data = file.read()
    attachment_part = MIMEApplication(attachment_data, Name="daily_deals.pdf")
    attachment_part["Content-Disposition"] = f"attachment; filename=daily_deals.pdf"
    msg.attach(attachment_part)

    # Send the email using SMTP
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(email, password)
        smtp.send_message(msg)
        print("Email sent successfully!")


def job():
    try:
        logging.info("Starting job...")
        results = search_newegg(NEWEGG_URL)
        pdf_file = generate_pdf(results)
        send_email(
            "Daily Deals Results",
            "Please see attached PDF file for the daily deals",
            pdf_file,
        )
        logging.info("Job completed successfully.")
    except Exception as e:
        logging.error(f"Job failed: {e}")


def main():
    job()


if __name__ == "__main__":
    main()
