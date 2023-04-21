import pprint
import time
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome

from father import FatherBot


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
            # if "2awarehouse.com" in url:
            #     self.scrape_warehouse_2a(url)
            # if "ammunitiondepot.com" in url:
            #     self.scrape_ammunition_depot(url)
            # if "luckygunner.com" in url:
            #     self.scrape_lucky_gunner(url)

        self.results.sort(key=lambda x: int(x["cpr"]))
        self.results = self.results[:10]
        pprint.pprint(self.results)

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

            # If casing is brass and the title contains the word "steel", skip it.
            if (
                "steel" in result["title"].lower()
                and "steel" not in self.casing.lower()
            ):
                continue
            else:
                # If there are three prices, the second is the actual price and the third is the cpr.
                if len(prices) == 3:
                    try:
                        result["price"] = prices[1].text.strip()
                        result["cpr"] = prices[2].text.strip().replace("$0.", "")
                        self.results.append(result)
                    except ValueError:
                        continue
                elif len(prices) == 2:
                    try:
                        result["price"] = int(prices[0].text.strip())
                        result["cpr"] = prices[1].text.strip().replace("$0.", "")
                        self.results.append(result)
                    except ValueError:
                        continue

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
        for row in inner.find_all("li")[:8]:
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

            # If casing is brass and the title contains the word "steel", skip it.
            if (
                "steel" in result["title"].lower()
                and "steel" not in self.casing.lower()
            ):
                continue

            # If there are two prices, the first is the actual price and the second is the cpr.
            if len(prices) == 2:
                result["price"] = prices[0].strip()
                result["cpr"] = (
                    prices[1]
                    .strip()
                    .split(" ")[0]
                    .replace("0.", "")
                    .replace("0", "", 1)
                )
                self.results.append(result)
            else:
                continue

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
                word
                for word in result["title"].split(" ")
                if word
                in [
                    "50RD",
                    "50rd",
                    "100RD",
                    "100rd",
                    "500RD",
                    "500rd",
                    "1000RD",
                    "1000rd",
                ]
            ]

            # If casing is brass and the title contains the word "steel", skip it.
            if (
                "steel" in result["title"].lower()
                and "steel" not in self.casing.lower()
            ):
                continue

            # If rounds information is found in the title, calculate and append CPR to the result dictionary
            if len(title_rounds) > 0:
                title_round = int(title_rounds[0].lower().split("r")[0])
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
