import requests
import logging
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Chrome
import time


class AmmoDealsBot:
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers
        self.results = []

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
    url = "https://palmettostatearmory.com/9mm-ammo.html?caliber_multi=9mm"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    bot = AmmoDealsBot(url, headers)
    bot.search()


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
