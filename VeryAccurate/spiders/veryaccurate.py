#-*- coding: utf-8 -*-
import json
import logging
import re
import time
from urllib.parse import urljoin
from urllib.request import urlretrieve

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import scrapy
from PIL import Image
from VeryAccurate.items import VeryaccurateItem
from lxml import etree
from pytesseract import pytesseract


class VeryaccurateSpider(scrapy.Spider):
    name = 'veryaccurate'
    allowed_domains = ['www.variflight.com']
    start_urls = ['http://www.variflight.com/']

    def start_requests(self):
        flight_num = getattr(self, 'flight_num',None)
        date = getattr(self,'date',None)
        url = f'http://www.variflight.com/flight/fnum/{flight_num}.html?AE71649A58c77&fdate={date}'
        yield scrapy.Request(url,callback=self.parse_page)

    def parse_page(self,response):
        item = VeryaccurateItem()
        headers = {
            # 'User-Agent': UserAgent().random,
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
            'Accept': "*/*",
            'Cache-Control': "no-cache",
            'Host': "www.variflight.com",
            'accept-encoding': "gzip, deflate",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
        }
        try:
            b = response.xpath('//*[@class="searchlist_innerli"]')
            if b:
                name = response.xpath('//*[@class="tit"]/h1/@title').extract_first().strip()
                log = "{0}航班存在信息...".format(name)
                print(log)

                mylist = response.xpath('//*[@id="list"]/li')
                #print(len(mylist))

                for selector in mylist:
                    cookies = response.headers.getlist('Set-Cookie')
                    cookie = {}
                    for each in cookies[1:]:
                        each = str(each, encoding='utf-8')
                        each = each.split(';')
                        key = each[0].split('=')[0].replace(' ', '')  # 记得去除空格
                        value = each[0].split('=')[1]
                        cookie[key] = value

                    a = selector.xpath('div[@class="li_com"]/span[1]/b/a//text()').extract()  # 航班信息
                    flight_company = a[0]
                    flight_num = a[1]

                    # 计划起飞
                    FlightDeptimePlan = selector.xpath('div[@class="li_com"]/span[2]/@dplan').extract_first()

                    # 实际起飞
                    FlightDeptime_img_link= selector.xpath('div[@class="li_com"]/span[6]/img/@src').extract_first()

                    # 实际到达
                    FlightArrtime_img_link = selector.xpath('div[@class="li_com"]/span[3]/img/@src').extract_first()

                    if FlightDeptime_img_link and FlightArrtime_img_link:
                        FlightDeptime_img_link = urljoin(response.url, FlightDeptime_img_link)
                        res = requests.get(FlightDeptime_img_link, headers=headers, cookies=cookie)
                        actual_start_time_filename = time.time()
                        with open(f'F:\\Pycharm_projects\\VeryAccurate\\VeryAccurate\\spiders\\pic\\{actual_start_time_filename}.jpg', 'wb') as f:
                            f.write(res.content)
                        image = Image.open(f"F:\\Pycharm_projects\\VeryAccurate\\VeryAccurate\\spiders\\pic\\{actual_start_time_filename}.jpg")
                        time1 = pytesseract.image_to_string(image)
                        _time1 = time1.split(":")[0].replace('0','')

                        FlightArrtime_img_link = urljoin(response.url, FlightArrtime_img_link)
                        res = requests.get(FlightArrtime_img_link, headers=headers, cookies=cookie)
                        actual_arrive_time_filename = time.time()
                        with open(
                                f'F:\\Pycharm_projects\\VeryAccurate\\VeryAccurate\\spiders\\pic\\{actual_arrive_time_filename}.jpg',
                                'wb') as f:
                            f.write(res.content)
                        image = Image.open(
                            f"F:\\Pycharm_projects\\VeryAccurate\\VeryAccurate\\spiders\\pic\\{actual_arrive_time_filename}.jpg")
                        time2 = pytesseract.image_to_string(image)
                        _time2 = time2.split(":")[0]

                        if  _time1 < _time2:
                            FlightDeptime = time1
                            FlightArrtime = time2

                        elif _time1 > _time2:
                            FlightDeptime = time2
                            FlightArrtime = time1

                    elif FlightDeptime_img_link and not FlightArrtime_img_link:
                        FlightDeptime_img_link = urljoin(response.url, FlightDeptime_img_link)
                        res = requests.get(FlightDeptime_img_link, headers=headers, cookies=cookie)
                        actual_start_time_filename = time.time()
                        with open(f'F:\\Pycharm_projects\\VeryAccurate\\VeryAccurate\\spiders\\pic\\{actual_start_time_filename}.jpg','wb') as f:
                            f.write(res.content)
                        image = Image.open(f"F:\\Pycharm_projects\\VeryAccurate\\VeryAccurate\\spiders\\pic\\{actual_start_time_filename}.jpg")
                        FlightDeptime = pytesseract.image_to_string(image)
                        FlightArrtime = '暂无信息'


                    elif FlightArrtime_img_link and not FlightDeptime_img_link :
                        FlightArrtime_img_link = urljoin(response.url, FlightArrtime_img_link)
                        res = requests.get(FlightArrtime_img_link, headers=headers, cookies=cookie)
                        actual_arrive_time_filename = time.time()
                        with open(
                                f'F:\\Pycharm_projects\\VeryAccurate\\VeryAccurate\\spiders\\pic\\{actual_arrive_time_filename}.jpg',
                                'wb') as f:
                            f.write(res.content)
                        image = Image.open(
                            f"F:\\Pycharm_projects\\VeryAccurate\\VeryAccurate\\spiders\\pic\\{actual_arrive_time_filename}.jpg")

                        FlightDeptime = pytesseract.image_to_string(image)
                        FlightArrtime = '暂无信息'

                    else:
                        FlightDeptime = '暂无信息'
                        FlightArrtime = '暂无信息'


                    # 出发地
                    FlightDep = selector.xpath('div[@class="li_com"]/span[4]/text()').extract_first()
                    FlightDepAirport = re.findall(r'[\u4e00-\u9fa5]+',FlightDep)[0] # 出发地

                    #登机口
                    FlightHTerminal = re.findall(r'T\d?\w',FlightDep)[0] if re.findall(r'T\d?\w',FlightDep) else ''

                    FlightArrtimePlan = selector.xpath('div[@class="li_com"]/span[5]/@aplan').extract_first()  # 计划到达



                    FlightArr = selector.xpath('div[@class="li_com"]/span[7]/text()').extract_first()
                    # 出发地
                    FlightArrAirport =re.findall(r'[\u4e00-\u9fa5]+',FlightArr)[0]

                    #降落出口
                    FlightTerminal = re.findall(r'T\d?\w',FlightArr)[0] if re.findall(r'T\d?\w',FlightArr) else ''

                    #准点率
                    OntimeRate_link = selector.xpath('div[@class="li_com"]/span[8]/img/@src').extract_first()
                    OntimeRate_link = urljoin(response.url,OntimeRate_link)
                    res = requests.get(OntimeRate_link, headers=headers, cookies=cookie)
                    ontimerate_filename = time.time()
                    with open(f'F:\\Pycharm_projects\\VeryAccurate\\VeryAccurate\\spiders\\pic\\{ontimerate_filename}.jpg','wb') as f:
                        f.write(res.content)
                    image = Image.open(f"F:\\Pycharm_projects\\VeryAccurate\\VeryAccurate\\spiders\\pic\\{ontimerate_filename}.jpg")
                    OntimeRate = pytesseract.image_to_string(image)

                    FlightState = selector.xpath('div[@class="li_com"]/span[9]/text()').extract_first()  # 状态

                    detail_url =selector.xpath('a[@class="searchlist_innerli"]/@href').extract_first()   #详情页
                    detail_url = urljoin(response.url,detail_url)
                    html = requests.get(detail_url,headers=headers)
                    html.encoding = 'utf-8'
                    soup = BeautifulSoup(html.text,'lxml')

                    #机型
                    generic= soup.select('li[class="mileage"] span')[0].text

                    #机龄
                    FlightYear = soup.select('li[class="time"] span')[0].text

                    #总里程
                    distance = soup.select('div[class="p_ti"] span')[0].text

                    #飞行时间
                    FlightDuration = soup.select('div[class="p_ti"] span')[0].next_sibling.next_sibling.get_text()
                    item["FlightCompany"] = flight_company
                    item["FlightNum"] = flight_num
                    item["FlightDeptimePlan"] = FlightDeptimePlan
                    item["FlightDeptime"] = FlightDeptime
                    item["FlightDepAirport"] = FlightDepAirport
                    item["FlightHTerminal"] = FlightHTerminal
                    item["FlightArrtimePlan"] = FlightArrtimePlan
                    item["FlightArrtime"] = FlightArrtime
                    item["FlightArrAirport"] = FlightArrAirport
                    item["FlightTerminal"] = FlightTerminal
                    item["OntimeRate"] = OntimeRate
                    item["FlightState"] = FlightState
                    item["generic"] = generic
                    item["FlightYear"] = FlightYear
                    item["distance"] = distance
                    item["FlightDuration"] = FlightDuration

                    yield item

            else:
                name = response.xpath('//*[@id="byNumInput"]/@value').extract_first()
                log = "{0}航班不存在信息...".format(name)
                print(log)

        except Exception as e:
            logging.error(f'程序出现异常!!!: {e}')























