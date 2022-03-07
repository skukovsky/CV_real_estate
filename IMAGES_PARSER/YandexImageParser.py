import requests
from fake_headers import Headers
from bs4 import BeautifulSoup
from selenium import webdriver
import json
from pathlib import Path
from tqdm.notebook import tqdm
import time

class YandexImageParser:
    def __init__(self):
        self.about = 'YandexImageParser'
        self.version = '0.0.1'

    def gather_image_links(self, query: str):
        images = []
        url = 'https://yandex.ru/images/search?from=tabbar&text=' + query.replace(' ', '%20') + '%20'
        browser = webdriver.Safari()
        browser.get(url)
        time.sleep(5)
        browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(5)
        browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(80)
        
        html = browser.page_source
        browser.close()
        soup = BeautifulSoup(html, 'lxml')
        items_place = soup.find('div', {"class": "serp-list"})
        if items_place:
            print(f'Everything is okay\nGathering images..')
            items = items_place.find_all("div", {"class": "serp-item"})
            for item in items:
                data = json.loads(item.get("data-bem"))
                try:
                    image_link = data['serp-item']['img_href']
                except:
                    try:
                        image_link = json.loads(item.get("data-bem"))['serp-item']['preview'][0]['origin']['url']
                    except:
                        image_link = json.loads(item.get("data-bem"))['serp-item']['preview'][1]['origin']['url']
                images.append(image_link)
        return set(images)

    def save_images(self, class_name: str, image_links: list()):
        class_name = class_name.replace(' ', '_')
        for image_number, link in tqdm(enumerate(image_links), total=len(image_links)):
            if image_number % 100 == 0:
                time.sleep(5)
            output_file = Path(f'../data/{class_name}/{class_name}_{image_number}.jpg') 
            output_file.parent.mkdir(exist_ok=True, parents=True)
            with open(output_file, 'wb') as handler:
                try:
                    handler.write(requests.get(link, headers=Headers(headers=True).generate()).content)
                except:
                    pass

    def run_parser(self, queries: list()):
        res = dict()
        for query in queries:
            res[query] = self.gather_image_links(query)
        for key, value in res.items():
            self.save_images(key, value)