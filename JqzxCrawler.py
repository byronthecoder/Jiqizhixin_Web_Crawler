"""
Created by Zheng Yuan -- 27th October, 2019
This code runs and tests on MacOS 10.14.5

Command for run the code:
    $ python Jqzx_Crawler.py

"""

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
from config import *
from HotTopics import *
import pymongo

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)


# Emulating the click action to load more web content
def load_more():
    try:
        load_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                 '#js-has-modal > div.u-container > div > div > span:nth-child(1) > div > div.u-loadmore > a')))
        load_button.click()

    except TimeoutException:
        return load_more()

# Get news title and save to a list
def get_title():
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#js-has-modal > div.u-container > div > div')))
        html = browser.page_source
        doc = pq(html)
        items = doc(
            'a').items()

        title = []
        for item in items:
            if str(item.attr('class')) == 'u-text-limit--two daily-every__title js-open-modal':
                title.append(item.text())

        return title
    except TimeoutException:
        return get_title()


# Get date of the page
def get_time():
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#js-has-modal > div.u-container > div > div')))
        html = browser.page_source
        doc = pq(html)
        items = doc(
            'span').items()

        for item in items:
            if str(item.attr('class')) == 'daily-every__month':
                month = item.text()
                print(month+'\n')

            elif str(item.attr('class')) == 'daily-every__day':
                day = item.text()
                print(day+'\n')

    except TimeoutException:
        return get_time()


# Get news content and save to a list
def get_content():
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#js-has-modal > div.u-container > div > div')))
        html = browser.page_source
        doc = pq(html)
        items = doc('div').items()

        content = []
        for item in items:
            if str(item.attr('class')) == 'u-text-limit--three daily__content':
                content.append(item.text())
        return content

    except TimeoutException:
        return get_content()


# Save news title and content to a dict and write to a txt file or database
def news_dict(title, content):
    if len(title) == len(content):
        print('Begin crawling...')

        kword_list = []
        for i in range(len(title)):
            keywords1 = jieba.analyse.extract_tags(content[i], topK=5, withWeight=True,
                                       allowPOS=('ns', 'n', 'nr', 'nt', 'un', 'vn', 'nz', 'j', 'Ng'))

            # Keywords extracted with Jieba's textrank algorithm, for comparision
            keywords2 = jieba.analyse.textrank(content[i], topK=5, withWeight=True,
                                   allowPOS=('ns', 'n', 'nr', 'nt', 'un', 'vn', 'nz', 'j', 'Ng'))

            news = {
                'title': title[i],
                'content': content[i],
                'keywords1': keywords1,
                'keywords2': keywords2
            }
            print(news)
            kword_list.append(news['keywords1'])

            with open('./news/news{}.txt'.format(i), 'w', encoding='utf-8') as f:
                print('Saving news{}...'.format(i))
                f.write(news['title'] + '\n'*2 + news['content'] + '\n'*2)
        print('News saved!\n')

        with open('./keywords.txt', 'w', encoding='utf-8') as f:
            for kwords in kword_list:
                for w in kwords:
                    f.write(w[0] + '\n')

            # save_to_mongo(news)
    else:
        print('Error: Title number and content number not match.')


# Save data to MongoDB database, optional
def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert_one(result):
            print("Save to MongoDB succeeded!", result)
    except Exception:
        print("Save to MongoDB failed", result)


# Pilot function: crawling with keyword search, modify all crawling methods to use
def search():
    try:
        browser.get('https://www.jiqizhixin.com/')
        search_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#js-site-search > div > a.header-search__btn.t-left > i")))
        search_button.click()
        input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#js-site-search > div > input")))
        input.send_keys('测试')
    except TimeoutException:
        return search()


def main():
    browser.get('https://www.jiqizhixin.com/dailies')
    try:
        # Loading to the chosen page_num
        for i in range(PAGE_NUM):
            load_more()

        # Begin to crawl
        title = get_title()
        content = get_content()
        news_dict(title, content)

        # Extract hot topics
        config_extractor(re_idf=False, ustop=True)
        with open('./keywords.txt', 'r', encoding='utf-8') as f:
            text = f.read()

        print("The hottest topics in a week are: \n")
        print(jieba.analyse.extract_tags(text, topK=10, withWeight=True,
                                         allowPOS=('ns', 'n', 'nr', 'nt', 'un', 'vn', 'nz', 'j', 'Ng')))

        # textrank algorithm
        # print(jieba.analyse.textrank(text, topK=5, withWeight=True,
        #                              allowPOS=('ns', 'n', 'nr', 'nt', 'un', 'vn', 'nz', 'j', 'Ng')))

    except Exception:
        print('MainError: Crawling failed!')
    finally:
        browser.close()




if __name__ == '__main__':
    main()

