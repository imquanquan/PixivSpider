#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import re
import os
import sys
import time
import requests
from bs4 import BeautifulSoup


class SagiriImg:
    def __init__(self,start,url,img_id):
        self.start = int(start)
        self.url = url
        self.img_id = img_id
        
    def __str__(self):
        return '%-5d%-10s%s' % (self.start,self.img_id,self.url)
    
    
class PixivSpider:
    def __init__(self,search,path,less_start = 0,crawl_page = 10):
        self.s = requests.session()
        self.path = path
        self.pixiv_url = 'https://www.pixiv.net'
        self.search_url = 'https://www.pixiv.net/search.php?word='+search+'&s_mode=s_tag_full&order=date_d&p='
        self.base_url = 'https://accounts.pixiv.net/login?return_to=https%3A%2F%2Fwww.pixiv.net%2F&lang=zh&source=accounts&view_type=page&ref='
        self.login_url = 'https://accounts.pixiv.net/api/login?lang=zh'
        self.img_list = []
        self.less_start = int(less_start)
        self.crawl_page = int(crawl_page)
        self.pixiv_id = 'imquanquan99'
        self.pixiv_password = 'mjm2mhq134'
        self.headers = {
            'Referer' : 'https://accounts.pixiv.net/login?return_to=https%3A%2F%2Fwww.pixiv.net%2F&lang=zh&source=accounts&view_type=page&ref=',
            'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
    
    def login(self):
        base_url_html = self.s.get(self.base_url, headers=self.headers).text
        base_url_soup = BeautifulSoup(base_url_html,'lxml')
        post_key = base_url_soup.find('input')['value']
        data = {
            'pixiv_id' : self.pixiv_id,
            'password' : self.pixiv_password ,
            'captcha' : '',
            'g_recaptcha_response': '',
            'post_key': post_key,
            'source' : 'accounts',
            'ref' : 'wwwtop_accounts_index',
            'return_to': 'https://www.pixiv.net/'
        }        
        self.s.post(self.login_url, data=data, headers=self.headers)
        
    def get_img_list(self):
        for page_num in range(self.crawl_page):
            list_img_page = self.s.get(self.search_url+str(page_num),headers=self.headers).text
            list_img_page_soup =  BeautifulSoup(list_img_page,'lxml')
            li_list = list_img_page_soup.find_all('li', attrs={'class', 'image-item'})
            for img_li in li_list:
                img_id = img_li.div.img['data-id']
                url = self.pixiv_url+img_li.a['href']
                try:
                    start = re.sub("\D","",img_li.li.a['data-tooltip'])
                except AttributeError:
                    start = '0'
                if int(start) >= self.less_start:
                    self.img_list.append(SagiriImg(start, url,img_id ))
                    print(SagiriImg(start, url,img_id ))
                    
    def download_img(self):
        os.chdir(self.path)
        img_re = re.compile(r'ui-modal-trigger.*?src="(.*?)" alt=')
        img_re1 = re.compile(r'e".*?src="(.*?)" alt=')
        for img in self.img_list:
            follow_url_html = self.s.get(img.url,headers=self.headers).text
            print(img.url)
            try:
                img_link = re.findall(img_re, follow_url_html)[0]
            except IndexError:
                img_link = re.findall(img_re1, follow_url_html)[0]
            except :
                pass
            if img_link:
                src_headers = self.headers
                src_headers['Referer'] = img.url
                image = requests.get(img_link, headers=src_headers).content
                with open(img.img_id + '.jpg', 'ab') as f:  
                    f.write(image)  
                time.sleep(2)            

                    
    def crawl(self):
        self.login()
        print(self.search_url)
        self.get_img_list()
        self.download_img()
        
        
        


if __name__ == "__main__":
    spider = PixivSpider(*sys.argv[1:])
    spider.crawl()
    

                
            
            
        
        