import requests
import smtplib
from decouple import config
from weasyprint import HTML
from jinja2 import Template
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


class FatherBot:
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers
        self.results = []

    def generate_pdf(self):
        with open("pdf.html") as file:
            template = Template(file.read())
        html = template.render(results=self.results)
        pdf_file = "daily_deals.pdf"
        HTML(string=html).write_pdf(pdf_file)
        return pdf_file

    def send_email(self, subject, message, attachment):
        recipients = ["tabeman3906@hotmail.com"]
        email = config("GMAIL_EMAIL")
        password = config("GMAIL_PASSWORD")
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = email
        msg["To"] = ", ".join(recipients)
        msg.attach(MIMEText(message))
        with open(attachment, "rb") as file:
            attachment_data = file.read()
        attachment_part = MIMEApplication(attachment_data, Name="daily_deals.pdf")
        attachment_part["Content-Disposition"] = f"attachment; filename=daily_deals.pdf"
        msg.attach(attachment_part)
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(email, password)
            smtp.send_message(msg)
            print("Email sent successfully!")

    def run(self):
        try:
            self.search()
            pdf_file = self.generate_pdf()
            self.send_email(
                "Daily Deals Results",
                "We've crawled the web and found the best deals for you! Please see the attached PDF for the results.",
                pdf_file,
            )
        except Exception as e:
            print(f"Error: {e}")


class NeweggDealsBot(FatherBot):
    def search(self):
        page = requests.get(self.url, headers=self.headers)
        soup = BeautifulSoup(page.content, "html.parser")
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
            result["price_savings"] = row.find(
                "li", {"class": "price-save"}
            ).text.strip()
            self.results.append(result)


class AmmoDealsBot(FatherBot):
    def search(self):
        driver = Chrome()

        # Navigate to the page
        driver.get(self.url)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        inner = soup.find("ol", {"class": "products list items product-items"})
        for row in inner.find_all("li", {"class": "item product product-item"}):
            result = {}
            result["title"] = row.find("a", {"class": "product-item-link"}).text.strip()
            result["link"] = row.find("a", {"class": "product-item-link"}).get("href")
            prices = row.find_all("span", {"class": "price"})
            if len(prices) == 3:
                result["price"] = prices[1].text.strip()
                result["cpr"] = prices[2].text.strip()
            else:
                result["price"] = prices[0].text.strip()
                result["cpr"] = prices[1].text.strip()
            self.results.append(result)

        driver.quit()


def main():
    palmetto_url = "https://palmettostatearmory.com/9mm-ammo.html?caliber_multi=9mm"
    newegg_bot = NeweggDealsBot(
        "https://www.newegg.com/todays-deals?cm_sp=Head_Navigation-_-Under_Search_Bar-_-Today%27s+Best+Deals&icid=720202",
        HEADERS,
    )
    newegg_bot.run()


if __name__ == "__main__":
    main()
