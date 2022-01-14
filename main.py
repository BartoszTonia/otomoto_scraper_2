from run_driver import run_driver
from bs4 import BeautifulSoup
from pathlib import Path
from time import sleep, time
import pandas as pd
import datetime
import requests
import re

# search_page = "https://www.otomoto.pl/osobowe/ford--nissan?search%5Bfilter_enum_fuel_type%5D=electric&search%5Bfilter_float_mileage%3Afrom%5D=50"
search_page = "https://www.otomoto.pl/osobowe?search%5Bfilter_enum_fuel_type%5D=electric&search%5Bfilter_float_mileage%3Afrom%5D=1000"
offers = [{'url': search_page}]     # save to file session_{}.csv
url_list = [search_page]    # save to file - links.txt


def count_pages( url ):
    search_pages_list = [url]
    first_page = requests.get(url)
    soup = BeautifulSoup(first_page.content, 'html.parser')
    try:
        count = soup.find_all('a', 'optimus-app-g4wbjr ekxs86z0')[-1].text
    except IndexError:
        count = 1
    first_page.close()
    sleep(3)
    page_number = 2
    while page_number <= int(count):
        next_page = url + '&page=' + str(page_number)
        search_pages_list.append(next_page)
        page_number += 1

    sleep(3)
    return search_pages_list


def scrape_links_from( url ):
    page = run_driver(url)
    soup = BeautifulSoup(page.page_source, 'html.parser')
    href_bundle = soup.find_all('a', href=True)
    total_count = 0
    offers_count = 0
    for each in href_bundle:
        total_count += 1
        if "otomoto.pl/oferta" in str(each['href']) and "link=https://www.otomoto.pl/oferta/" not in str(each['href']):
            offers_count += 1
            if each['href'] not in url_list:
                url_list.append(each['href'])

    print(total_count, offers_count, len(url_list))
    page.close()
    sleep(4.9)


def extract_soup( soup ):
    descr = soup.find('div', 'offer-description__description').text
    price = soup.find('span', 'offer-price__number').text
    price = re.sub(r'\s', '', price).rstrip('PLN')

    offer = {'price': price}
    regex_list = ['(.*Zasięg.*)', '(.*zasięg.*)', '(.*Zasieg.*)', '(.*zasieg.*)', '(.*można przejechać.*)']
    for regex in regex_list:
        if re.findall(regex, descr):
            offer['distance'] = re.findall(regex, descr)
            print(offer['distance'])

    labels = soup.find_all('span', 'offer-params__label')
    values = soup.find_all('div', 'offer-params__value')
    for x in range(len(values)):
        label = re.split(r"\s", labels[x].text.lstrip('\n'))[0]
        value = re.sub(r"\s", '', values[x].text.lstrip('\n'))
        offer[label] = value

    return offer


def save_progress():
    # # # # # arrange columns # # # # #
    keys = []  # database columns
    for each in offers:
        for key, value in each.items():
            if key not in keys:
                keys.append(key)

    df = pd.DataFrame(columns=keys)  # create database with offer dictionary keys as columns

    # # # # # add offers to database and save # # # # #
    for each in offers:
        # if each['url'] not in df['url']:
        df = df.append(each, ignore_index=True)

    df.to_csv(Path('out/session.csv'))


def main():
    # # # # # gather all links into 'url_list' # # # # #
    total_pages = count_pages(search_page)
    print(len(total_pages), ' pages found')
    for page in total_pages:
        sleep(3)
        scrape_links_from(page)
        with open(Path('out/links.txt'), 'w') as file:
            file.write('\n'.join(url_list))

    # # # # # (Optional) Read from file  # # # # #
    # with open(Path('out/links.txt'), 'r') as file:
    #     url_list = file.read().split('\n')
    #     print(url_list)

    # # # # # scrape data from 'url_list' links # # # # #
    for url in url_list:
        response = run_driver(url)
        offer_soup = BeautifulSoup(response.page_source, 'html.parser')
        try:
            offer = extract_soup(offer_soup)
        except AttributeError:
            print('>>>>>>>>>>Attribute Error<<<<<<<<<<<< - offer does not exist')
            offer = {}
        offer['url'] = url
        offers.append(offer)
        response.close()
        print(offer)
        save_progress()
        sleep(1.3)

    t = time()
    timestamp = datetime.datetime.fromtimestamp(t)
    print(timestamp.strftime("%Y-%m-%d %H:%M:%S"))
    print('>> total offers >> ', len(url_list), len(offers))

main()
