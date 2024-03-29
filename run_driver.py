from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from time import sleep
import requests


options = Options()
options.add_argument('headless')
options.add_experimental_option('excludeSwitches', ['enable-logging'])  # hides DevTools output in console


def run_driver(url):
    service = Service("driver\chromedriver.exe")
    driver = webdriver.Chrome(options=options, service=service)

    try:
        driver.get(url)
    except WebDriverException:
        sleep(7.5)
        print(' >>>>> second try')
        try:
            driver.get(url)
        except WebDriverException:
            sleep(3.2)
            print("failed, return driver")
            return run_driver(url)

    print('>>> ', driver.title, end=' - ')

    try:
        delay = 3
        price_selector = '#description'
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, price_selector)))
    except TimeoutException:
        print('...', end=' ')
        sleep(2.3)
        try:
            delay = 3
            price_selector = '#page-header > div > div.optimus-app-70qvj9 > div > a > img'
            WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, price_selector)))
        except TimeoutException:
            print('---', end=' ')
            sleep(2.3)

    return driver
