import requests
import smtplib
import time
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
    """
    A base class for web scraping bots that crawl websites and generate daily deals reports in PDF format.
    """

    def __init__(self, urls, headers=None):
        """
        Initializes a new instance of the FatherBot class.

        Args:
            url (str): The URL of the website to crawl.
            headers (dict): A dictionary of HTTP headers to send with each request.
        """
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


class NeweggDealsBot(FatherBot):
    """
    A web scraping bot that crawls newegg.com for daily deals and generates a report in PDF format.

    Inherits from the FatherBot class.
    """

    def search(self):
        """
        Scrapes newegg.com for daily deals and populates the results list.

        Returns:
            str: The name of the website that was searched.
        """
        # Send a GET request to the website and parse the HTML content with BeautifulSoup
        page = requests.get(self.urls, headers=self.headers)
        soup = BeautifulSoup(page.content, "html.parser")

        # Find the section of the page with the daily deals and loop through each item
        inner = soup.find("div", {"class": "item-cells-wrap tile-cells five-cells"})
        for row in inner.find_all("div", {"class": "item-cell"}):
            result = {}
            # Extract the relevant information for each deal and add it to the results dictionary
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

        # Return name of website for use in the generate_pdf() method
        return "newegg"


class AmmoDealsBot(FatherBot):
    """
    A web scraping bot that crawls targetsportsusa.com and palmettostatearmory.com for ammo deals.

    Inherits from the FatherBot class.
    """

    def search(self):
        """
        Executes web scraping on each URL in self.urls, then sorts the results by cpr and returns "ammo".
        """
        for url in self.urls:
            if "targetsportsusa.com" in url:
                self.scrape_target_sports(url)
            if "palmettostatearmory.com" in url:
                self.scrape_palmetto(url)
            if "2awarehouse.com" in url:
                self.scrape_warehouse_2a(url)
            if "www.ammunitiondepot.com" in url:
                self.scrape_ammunition_depot(url)

        self.results.sort(key=lambda x: int(x["cpr"]))
        self.results = self.results[:10]

        # Return name of website for use in the generate_pdf() method
        return "ammo"

    def scrape_palmetto(self, url):
        """
        Scrapes palmettostatearmory.com for ammo deals.

        Appends a dictionary containing the title, link, price, and cpr of each deal to self.results.
        """
        driver = Chrome()

        # Navigate to the page
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        inner = soup.find("ol", {"class": "products list items product-items"})
        for row in inner.find_all("li", {"class": "item product product-item"}):
            result = {}
            result["title"] = row.find("a", {"class": "product-item-link"}).text.strip()
            result["link"] = row.find("a", {"class": "product-item-link"}).get("href")
            prices = row.find_all("span", {"class": "price"})
            if len(prices) == 3:
                # If there are three prices, the second is the actual price and the third is the cpr.
                result["price"] = prices[1].text.strip()
                result["cpr"] = prices[2].text.strip().replace("$0.", "")
            else:
                # If there are only two prices, the first is the actual price and the second is the cpr.
                result["price"] = prices[0].text.strip()
                result["cpr"] = prices[1].text.strip().replace("$0.", "")
            self.results.append(result)

        driver.quit()

    def scrape_target_sports(self, url):
        """
        Scrapes targetsportsusa.com for ammo deals.

        Appends a dictionary containing the title, link, price, and cpr of each deal to self.results.
        """
        driver = Chrome()

        # Navigate to the page
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        inner = soup.find("div", {"class": "ResultsArea"}).find(
            "ul", {"class": "product-list"}
        )
        for row in inner.find_all("li")[:15]:
            result = {}
            result["title"] = row.find("h2").text.strip()
            link = row.find("a").get("href")
            result["link"] = f"https://www.targetsportsusa.com{link}"
            prices = list(
                filter(
                    lambda x: x != "",
                    row.find("div", {"class": "product-listing-price"})
                    .text.strip()
                    .rsplit("$", 1),
                )
            )
            if len(prices) == 2:
                # If there are two prices, the first is the actual price and the second is the cpr.
                result["price"] = prices[0].strip()
                result["cpr"] = (
                    prices[1]
                    .strip()
                    .split(" ")[0]
                    .replace("0.", "")
                    .replace("0", "", 1)
                )
                self.results.append(result)

        driver.quit()

    def scrape_warehouse_2a(self, url):
        """
        Scrapes ammunition products from 2awarehouse.com.

        Args:
            url (str): The URL to scrape.

        Returns:
            None. Appends a dictionary of information about each ammunition product to self.results.
        """
        driver = Chrome()

        # Navigate to the page
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        inner = soup.find("ul", {"class": "productGrid productGrid--maxCol3"})

        # Iterate over each product listed on the page
        for row in inner.find_all("li", {"class": "product"}):
            result = {}
            result["title"] = (
                row.find("h4", {"class": "card-title"}).find("a").text.strip()
            )
            result["link"] = (
                row.find("h4", {"class": "card-title"}).find("a").get("href")
            )
            result["price"] = row.find(
                "span", {"class": "price price--withoutTax price--main"}
            ).text.strip()
            price = float(result["price"].replace("$", ""))

            # Find the rounds information in the product title
            title_rounds = [
                word for word in result["title"].split(" ") if word in ["50RD", "100RD"]
            ]

            # If rounds information is found in the title, calculate and append CPR to the result dictionary
            if len(title_rounds) > 0:
                title_round = int(title_rounds[0].split("R")[0])
                result["cpr"] = str(round(float(price / title_round), 2)).replace(
                    "0.", ""
                )
                self.results.append(result)
            else:
                # If rounds information is not found, skip this product
                continue

        driver.quit()

    def scrape_ammunition_depot(self, url):
        """
        Scrapes ammunition products from ammunitiondepot.com.

        Args:
            url (str): The URL to scrape.

        Returns:
            None. Appends a dictionary of information about each ammunition product to self.results.
        """
        driver = Chrome()

        # Navigate to the page
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        inner = soup.find(
            "div",
            {"id": "searchspring-content"},
        ).find(
            "ol",
            {
                "class": "ss-item-container products list items product-items ss-targeted"
            },
        )

        # Iterate over each product listed on the page
        for row in inner.find_all(
            "li", {"class": "ss-item item product product-item ng-scope"}
        ):
            try:
                result = {}
                result["title"] = row.find(
                    "a", {"class": "product-item-link ng-binding"}
                ).text.strip()
                result["link"] = row.find(
                    "a", {"class": "product-item-link ng-binding"}
                ).get("href")
                result["price"] = row.find(
                    "span", {"class": "ng-binding ss-sale-price"}
                ).text.strip()

                # Extract CPR information from product description
                result["cpr"] = (
                    row.find("span", {"class": "rounds-price ng-scope"})
                    .text.strip()
                    .split(".")[1]
                    .split("per")[0]
                )
                self.results.append(result)
            except AttributeError:
                # If product information cannot be found, skip this product
                continue

        driver.quit()

    def scrape_lucky_gunner(self, url):
        """
        Scrapes luckygunner.com and extracts data on ammo products.

        Args:
            url (str): The URL of the luckygunner.com page to scrape.

        Returns:
            None.
        """
        driver = Chrome()

        # Navigate to the page
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Find the section of the page that contains the products
        inner = soup.find("ol", {"class": "products-list"})

        # Extract data for each product
        for row in inner.find_all("li", {"class": "item"}):
            try:
                result = {}
                result["title"] = (
                    row.find("h3", {"class": "product-name"}).find("a").text.strip()
                )
                result["link"] = (
                    row.find("h3", {"class": "product-name"}).find("a").get("href")
                )
                result["price"] = (
                    row.find("p", {"class": "special-price"})
                    .find("span", {"class": "price"})
                    .text.strip()
                )
                result["cpr"] = (
                    row.find("p", {"class": "cprc"}).text.strip().split(".")[0]
                )
                self.results.append(result)
            except (AttributeError, TypeError):
                # If product information cannot be found, skip this product
                continue

        driver.quit()


def main():
    answer = (
        input("Which site would you like to crawl? (newegg or ammo) ").lower().strip()
    )
    if answer == "newegg":
        newegg_url = config("NEWEGG_URL")
        newegg_bot = NeweggDealsBot(newegg_url, HEADERS)
        newegg_bot.run()
    else:
        lucky_gunner_url = config("LUCKY_GUNNER_URL")
        ammunition_depot_url = config("AMMUNITION_DEPOT_URL")
        warehouse_2a_url = config("WAREHOUSE_2A_URL")
        palmetto_url = config("PALMETTO_URL")
        targets_sports_ammo_url = config("TARGET_SPORTS_AMMO_URL")
        urls = [
            targets_sports_ammo_url,
            palmetto_url,
            warehouse_2a_url,
            ammunition_depot_url,
            lucky_gunner_url,
        ]
        ammo_bot = AmmoDealsBot(urls, HEADERS)
        ammo_bot.run()


if __name__ == "__main__":
    main()
