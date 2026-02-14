from __future__ import annotations

import datetime
import json
import re
from pathlib import Path
from time import sleep, time

import pandas as pd
import requests
from bs4 import BeautifulSoup

from run_driver import BrowserSession

# search_page = "https://www.otomoto.pl/osobowe/mercedes-benz/s-klasa/od-2004?search%5Bfilter_float_year%3Ato%5D=2011"
search_page = "https://www.otomoto.pl/osobowe?search%5Bfilter_enum_fuel_type%5D=electric&search%5Bfilter_float_mileage%3Afrom%5D=1000"
offers = [{"url": search_page}]  # save to file session.csv
url_list = [search_page]  # save to file - links.txt
OUTPUT_DIR = Path("out")


def count_pages(url: str) -> list[str]:
    search_pages_list = [url]
    response = requests.get(url, timeout=20)
    soup = BeautifulSoup(response.content, "html.parser")

    total_pages = 1
    for anchor in soup.find_all("a", href=True):
        href = anchor.get("href", "")
        match = re.search(r"[?&]page=(\d+)", href)
        if match:
            total_pages = max(total_pages, int(match.group(1)))

    for page_number in range(2, total_pages + 1):
        search_pages_list.append(f"{url}&page={page_number}")

    return search_pages_list


def scrape_links_from(page_html: str) -> None:
    soup = BeautifulSoup(page_html, "html.parser")
    href_bundle = soup.find_all("a", href=True)
    total_count = 0
    offers_count = 0

    for anchor in href_bundle:
        total_count += 1
        href = anchor["href"]
        href = f"https://www.otomoto.pl{href}" if href.startswith("/") else href

        if "https://www.otomoto.pl/oferta/" in href and "link=https://www.otomoto.pl/oferta/" not in href:
            offers_count += 1
            if href not in url_list:
                url_list.append(href)

    print(total_count, offers_count, len(url_list))


def extract_soup(soup: BeautifulSoup) -> dict[str, str | list[str]]:
    offer: dict[str, str | list[str]] = {}

    jsonld = soup.find("script", attrs={"type": "application/ld+json"})
    if jsonld and jsonld.text:
        try:
            data = json.loads(jsonld.text)
            if isinstance(data, dict):
                price = data.get("offers", {}).get("price")
                if price:
                    offer["price"] = str(price)
                brand = data.get("brand", {}).get("name")
                model = data.get("model")
                if brand:
                    offer["Marka"] = str(brand)
                if model:
                    offer["Model"] = str(model)
        except json.JSONDecodeError:
            pass

    desc_node = soup.select_one('[data-testid="content-description"]') or soup.find(
        "div", class_=re.compile("description", re.IGNORECASE)
    )
    description = desc_node.get_text(" ", strip=True) if desc_node else ""

    if "price" not in offer:
        price_node = soup.select_one('[data-testid="ad-price"]') or soup.find(
            "span", class_=re.compile("price", re.IGNORECASE)
        )
        if price_node:
            offer["price"] = re.sub(r"\D", "", price_node.get_text())

    regex_list = [
        r"(.*Zasięg.*)",
        r"(.*zasięg.*)",
        r"(.*Zasieg.*)",
        r"(.*zasieg.*)",
        r"(.*można przejechać.*)",
        r"(.*Ładuje.*)",
        r"(.*ładuje.*)",
        r"(.*ładowani.*)",
    ]

    for pattern in regex_list:
        matches = re.findall(pattern, description)
        if matches:
            offer["distance"] = matches
            break

    labels = soup.select('[data-testid="advert-details-item-label"]')
    values = soup.select('[data-testid="advert-details-item-value"]')
    for label_node, value_node in zip(labels, values, strict=False):
        label = re.split(r"\s", label_node.get_text(strip=True))[0]
        value = value_node.get_text(" ", strip=True)
        offer[label] = value

    return offer


def save_progress() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    keys: list[str] = []
    for each in offers:
        for key in each.keys():
            if key not in keys:
                keys.append(key)

    df = pd.DataFrame(columns=keys)
    for each in offers:
        df = df._append(each, ignore_index=True)

    df.to_csv(OUTPUT_DIR / "session.csv", index=False)


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    session = BrowserSession(headless=True)
    try:
        total_pages = count_pages(search_page)
        print(len(total_pages), " pages found")

        for page_url in total_pages:
            _, html = session.fetch_html(page_url)
            scrape_links_from(html)
            (OUTPUT_DIR / "links.txt").write_text("\n".join(url_list), encoding="utf-8")
            sleep(1)

        for url in url_list:
            _, html = session.fetch_html(url)
            offer_soup = BeautifulSoup(html, "html.parser")
            try:
                offer = extract_soup(offer_soup)
            except AttributeError:
                print(">>>>>>>>>>Attribute Error<<<<<<<<<<<< - offer does not exist")
                offer = {}
            offer["url"] = url
            offers.append(offer)
            print(offer)
            save_progress()
            sleep(0.5)
    finally:
        session.close()

    t = time()
    timestamp = datetime.datetime.fromtimestamp(t)
    print(timestamp.strftime("%Y-%m-%d %H:%M:%S"))
    print(">> total offers >> ", len(url_list), len(offers))


if __name__ == "__main__":
    main()
