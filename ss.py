import requests
import logging
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Chrome
import time


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
            if "targetsportsusa.com" in url:
                self.scrape_target_sports(url)
            if "palmettostatearmory.com" in url:
                self.scrape_palmetto(url)

        self.results.sort(key=lambda x: int(x["cpr"]))
        self.results = self.results[:10]

        print(self.results)

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


def main():
    palmetto_url = "https://palmettostatearmory.com/9mm-ammo.html?caliber_multi=9mm"
    targets_sports_ammo_url = "https://www.targetsportsusa.com/9mm-luger-ammo-c-51.aspx"
    urls = [palmetto_url, targets_sports_ammo_url]
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

# import requests
# import logging
# from bs4 import BeautifulSoup


# class AmmoDealsBot:
#     def __init__(self, url, headers):
#         self.url = url
#         self.headers = headers
#         self.results = []
#         self.logger = logging.getLogger(__name__)

#     def search(self):
#         try:
#             page = requests.get(self.url, headers=self.headers)
#         except requests.exceptions.RequestException as e:
#             self.logger.exception("Error making request: %s", e)
#             return

#         soup = BeautifulSoup(page.content, "html.parser")
#         top_deal = soup.find(
#             "div", {"id": "widget-042c7939-f091-4960-b527-4f8ddb10d77b"}
#         )
#         for row in top_deal.find_all("div", {"class": "wf-offer-content"})[:8]:
#             result = {}
#             result["title"] = row.find(
#                 "a", {"class": "wf-offer-link v-line-clamp"}
#             ).text.strip()
#             link = row.find("a", {"class": "wf-offer-link v-line-clamp"}).get("href")
#             result["link"] = f"https://www.bestbuy.com{link}"
#             price_div = row.find(
#                 "div", {"class": "priceView-hero-price priceView-customer-price"}
#             )
#             print(price_div)
#             if price_div:
#                 result["price"] = price_div.find("span").text.strip()
#             else:
#                 result["price"] = "N/A"
#             # result["price_savings"] = row.find(
#             #     "div",
#             #     {
#             #         "class": "pricing-price__savings pricing-price__savings--promo-red"
#             #     }.text.strip(),
#             # )
#             self.results.append(result)
#             print(self.results)


# def main():
#     logging.basicConfig(
#         filename="bot2.log",
#         level=logging.DEBUG,
#         format="%(asctime)s - %(levelname)s - %(message)s",
#     )

#     url = "https://www.bestbuy.com/site/misc/deal-of-the-day/pcmcat248000050016.c?id=pcmcat248000050016"
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
#         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
#         "Accept-Language": "en-US,en;q=0.5",
#         "Accept-Encoding": "gzip, deflate, br",
#         "Connection": "keep-alive",
#         "Upgrade-Insecure-Requests": "1",
#     }

#     bot = AmmoDealsBot(url, headers)
#     bot.search()


# if __name__ == "__main__":
#     main()
