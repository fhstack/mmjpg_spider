#!/usr/bin/env python
# coding=utf-8

import requests
from lxml import etree
import os
import sys
reload(sys)
sys.setdefaultencoding("utf8")
import time

from selenium import webdriver

chrome_options = webdriver.ChromeOptions()
#让Chrome不加载图片
prefs = {"profile.managed_default_content_settings.images":2}
chrome_options.add_experimental_option("prefs",prefs)
#无界面
chrome_options.add_argument("--headless")
chrome_options.add_argument('--no-sandbox')
chrome_path = '/usr/bin/chromedriver'
#储存路径
PICTURES_PATH = os.path.join(os.getcwd(),'picturs/')


headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/65.0.3325.181 Safari/537.36',
    'Referer': "http://www.mmjpg.com"
}

class Spider(object):
    #爬1~page_num页
    def __init__(self, page_num):
        self.page_num = page_num
        self.page_urls = ['http://www.mmjpg.com/'] #首页特殊处理
        self.girl_urls = []
        self.girl_name = ''
        self.pic_urls = []

    #从page_url中抓取所有妹子的url，放入girl_urls中
    #在网页中找到妹子的url在哪个标签
    def get_girl_urls(self):
        for page_url in self.page_urls:
            html = requests.get(page_url).content
            #print html
            selector = etree.HTML(html)
            #所有span路径下的class = 'title'下的a标签的href属性
            self.girl_urls += (selector.xpath('//span[@class="title"]/a/@href'))
            

    #若干个页面url
    def get_page_urls(self):
        if int(page_num) > 1:
            for n in range(2,int(page_num)+1):
                page_url = 'http://www.mmjpg.com/home/' + str(n)
                self.page_urls.append(page_url)
        elif int(page_num) == 1:
            pass


    #通过girl_urls获取所有图片的url，放入pic_urls中
    #有两个方式获取所有图片的url
    #1.遍历（下一页跳转）
    #2.网页上有个全部图片按钮，点击这个按钮可以显示所有图片
    #所有的pic_url会全部出来，我们通过selenium来模拟点击“全部图片”
    def get_pic_urls(self):
        driver = webdriver.Chrome(chrome_path,chrome_options = chrome_options)
        for girl_url in self.girl_urls:
            driver.get(girl_url)
            time.sleep(2)   #不要爬太快了，一方面不道德，一方面容易被Ban
            driver.find_element_by_xpath('//em[@class="ch all"]').click()
            time.sleep(2)   #获取上一步点击后的源码
            html = driver.page_source
            selector = etree.HTML(html)
            self.girl_name = selector.xpath('//div[@class="article"]/h2/text()')[0]
            self.pic_urls = selector.xpath('//div[@class="content"]/img/@data-img')
            try:
                self.download_pic()
            except Exception as e:
                print("{}保存失败".format(self.girl_name) + str(e))
    
    #下载图片
    def download_pic(self):
        try:
            os.mkdir(PICTURES_PATH)
        except:
            pass
        
        girl_path = PICTURES_PATH +self.girl_name
        try:
            os.mkdir(girl_path)
        except Exception as e:
            print("{}已存在".format(self.girl_name))
        img_th = 0;
        for pic_url in self.pic_urls:
            img_th += 1
            img_data = requests.get(pic_url,headers = headers)
            pic_path = girl_path + '/' + str(img_th) + '.jpg'
            if(os.path.isfile(pic_path)):
                print("{}第{}张已经存在".format(self.girl_name, img_th))
            else:
                with open(pic_path,'wb') as f:
                    f.write(img_data.content)
                    print("正在保存{}第{}张".format(self.girl_name,img_th))
                    f.close()

    def start(self):
        self.get_page_urls()
        self.get_girl_urls()
        self.get_pic_urls()


if __name__ == '__main__':
    page_num = input("你希望爬多少页？")
    mmjpg_spider = Spider(page_num)
    mmjpg_spider.start()

