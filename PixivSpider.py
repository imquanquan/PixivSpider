#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-12-14 16:10:17
# Project: Pixiv

from collections import namedtuple
import os
import requests

from pyspider.libs.base_handler import *


PIXIV_ID = 'pixiv_id'
PIXIV_PASSWORD = 'password'
SEARCH = 'エロマンガ先生'
BASE_URL = 'https://www.pixiv.net/'
LOGIN_PAGE_URL = 'https://accounts.pixiv.net/login'
LOGIN_API_URL = 'https://accounts.pixiv.net/api/login?lang=zh'
SAVE_PATH = '/home/imquanquan/sagiri'
MIN_START = 1000
MAX_PAGE = 255


PixivImage = namedtuple('PixivImage', ['title', 'art', 'start', 'url'])


class Handler(BaseHandler):
    crawl_config = {
        'headers' : {
            'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36' ,
            'Referer' : BASE_URL 
        }
    }

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl(LOGIN_PAGE_URL, callback=self.login_page)

    @config(age=10 * 24 * 60 * 60)
    def login_page(self, response):
        post_key = response.doc('input[name^="post_key"]').attr['value']
        data = {
            'pixiv_id' : PIXIV_ID ,
            'password' : PIXIV_PASSWORD ,
            'captcha' : '' ,
            'g_recaptcha_response': '' ,
            'post_key': post_key ,
            'source' : 'accounts',
            'ref' : 'wwwtop_accounts_index' ,
            'return_to': 'https://www.pixiv.net/'
        } 
        self.crawl(LOGIN_API_URL, callback = self.index_page, method = 'POST', data = data, cookies = response.cookies)
            
    @config(priority=2)
    def index_page(self, response):
        for page in range(MAX_PAGE+1):
            search_url = 'https://www.pixiv.net/search.php?s_mode=s_tag&word=' + str(SEARCH) + '&order=date_d&p=' + str(page)
            headers = {
            'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36' ,
            'Referer' : search_url 
        }
            self.crawl(search_url, callback = self.list_page, cookies = response.cookies, fetch_type = 'js', headers = headers, save = response.cookies)
        
    def list_page(self, response):
        print(response.save)
        for each in response.doc('figcaption').items():
            links = list(each('ul li a').items())
            try:
                start = int(links[2].text())
            except IndexError:
                start = 0
            if start > MIN_START:
                title = links[0].text()
                art = links[1].text()
                url = links[0].attr['href']
                headers = {
                    'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36' ,
                    'Referer' : url ,
                    'Origin' : 'https://www.pixiv.net'
                }
                image = PixivImage(title, art, start, url)
                self.crawl(url, callback = self.image_page, cookies = response.save, fetch_type = 'js', headers = headers, save = {'image' : image, 'cookies' : response.save})
      
    def image_page(self, response):
        os.chdir(SAVE_PATH)
        headers = {
                    'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36' ,
                    'Referer' : response.save['image'][3] ,
                }
        image_url = response.doc('.wrapper img').attr['data-src']
        file_name = response.save['image'][0] + '-' + response.save['image'][0] + '.png'
        if image_url:
            image = requests.get(image_url, headers=headers).content
            with open(file_name, 'wb') as f:
                f.write(image)
        else:
            image_url = response.doc('._layout-thumbnail img').attr['src']
            image = requests.get(image_url, headers=headers).content
            with open(file_name, 'wb') as f:
                f.write(image)
