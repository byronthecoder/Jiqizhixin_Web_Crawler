from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
from config import *
import pymongo


def get_news():
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#js-has-modal > div.u-container > div > div')))
        html = browser.page_source
        doc = pq(html)
        items = doc('div').items()

        for item in items:
            news = dict()
            if str(item.attr('class')) == 'u - text - limit - -two daily - every__title js - open - modal':

                news['title'] = item.text()

            elif str(item.attr('class')) == 'u-text-limit--three daily__content':
                news['content'] = item.text()

            print(news)

    except TimeoutException:
        return get_news()