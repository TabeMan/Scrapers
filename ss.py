import requests
import logging
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Chrome
import time
import pprint


class AmmoDealsBot:
    def __init__(self, urls, headers):
        self.urls = urls
        self.headers = headers
        self.results = []

    def search(self):
        """
        Executes web scraping on each URL in self.urls, then sorts the results by cpr and returns "ammo".
        """
        for url in self.urls:
            # if "targetsportsusa.com" in url:
            #     self.scrape_target_sports(url)
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
        driver = Chrome()

        # Navigate to the page
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        inner = soup.find("ul", {"class": "productGrid productGrid--maxCol3"})
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
            title_rounds = [
                word for word in result["title"].split(" ") if word in ["50RD", "100RD"]
            ]
            if len(title_rounds) > 0:
                title_round = int(title_rounds[0].split("R")[0])
                result["cpr"] = str(round(float(price / title_round), 2)).replace(
                    "0.", ""
                )
                self.results.append(result)
            else:
                continue

        driver.quit()

    def scrape_ammunition_depot(self, url):
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
                result["cpr"] = (
                    row.find("span", {"class": "rounds-price ng-scope"})
                    .text.strip()
                    .split(".")[1]
                    .split("per")[0]
                )
                self.results.append(result)
            except AttributeError:
                continue

        driver.quit()

    def scrape_lucky_gunner(self, url):
        driver = Chrome()

        # Navigate to the page
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        inner = soup.find("ol", {"class": "products-list"})
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
                print(result["price"])
                result["cpr"] = (
                    row.find("p", {"class": "cprc"}).text.strip().split(".")[0]
                )
                self.results.append(result)
            except (AttributeError, TypeError):
                continue

        driver.quit()


def main():
    lucky_gunner_url = "https://www.luckygunner.com/handgun/9mm-ammo"
    ammunition_depot_url = "https://www.ammunitiondepot.com/288-9mm"
    warehouse_2a_url = (
        "https://2awarehouse.com/ammo/pistol-ammo/9mm-luger/?_bc_fsnf=1&in_stock=1"
    )
    palmetto_url = "https://palmettostatearmory.com/9mm-ammo.html"
    targets_sports_ammo_url = "https://www.targetsportsusa.com/9mm-luger-ammo-c-51.aspx"
    urls = [
        palmetto_url,
        targets_sports_ammo_url,
        warehouse_2a_url,
        ammunition_depot_url,
        lucky_gunner_url,
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    bot = AmmoDealsBot(urls, headers)
    bot.search()
    # top_ten = bot.get_top_ten_deals()
    # print(top_ten)


if __name__ == "__main__":
    main()


# class NeweggDealsBot(FatherBot):
#     """
#     A web scraping bot that crawls newegg.com for daily deals and generates a report in PDF format.

#     Inherits from the FatherBot class.
#     """

#     def search(self):
#         """
#         Scrapes newegg.com for daily deals and populates the results list.

#         Returns:
#             str: The name of the website that was searched.
#         """
#         # Send a GET request to the website and parse the HTML content with BeautifulSoup
#         page = requests.get(self.urls, headers=self.headers)
#         soup = BeautifulSoup(page.content, "html.parser")

#         # Find the section of the page with the daily deals and loop through each item
#         inner = soup.find("div", {"class": "item-cells-wrap tile-cells five-cells"})
#         for row in inner.find_all("div", {"class": "item-cell"}):
#             result = {}
#             # Extract the relevant information for each deal and add it to the results dictionary
#             result["title"] = row.find("a", {"class": "item-title"}).text.strip()
#             result["link"] = row.find("a", {"class": "item-title"}).get("href")
#             result["price_was"] = row.find("li", {"class": "price-was"}).text.strip()
#             result["price_current"] = (
#                 row.find("li", {"class": "price-current"})
#                 .text.strip()
#                 .split("–")[0]
#                 .replace("\xa0", "")
#             )
#             result["price_savings"] = row.find(
#                 "li", {"class": "price-save"}
#             ).text.strip()
#             self.results.append(result)

#         # Return name of website for use in the generate_pdf() method
#         return "newegg"
