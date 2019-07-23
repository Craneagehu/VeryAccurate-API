#-*- coding: utf-8 -*-
import json
import re
import time
import threading
from urllib.parse import urljoin
from urllib.request import urlretrieve

import pymysql
from pyquery import PyQuery as pq
import requests
from PIL import Image
from bs4 import BeautifulSoup
from lxml import etree
from fake_useragent import UserAgent
from pytesseract import pytesseract
from requests.cookies import RequestsCookieJar


class VeryAccurate(object):
    def __init__(self,flightnum,date):
        self.Info = []
        self.flightnum = flightnum.upper()
        self.date = date

        self.start_url = f"http://www.variflight.com/flight/fnum/{self.flightnum}.html?AE71649A58c77&fdate={self.date}"
        self.ua = UserAgent()
        self.headers = {
            'User-Agent': self.ua.random,
            'Accept': "*/*",
            'Cache-Control': "no-cache",
            'Host': "www.variflight.com",
            'accept-encoding': "gzip, deflate",
            'Connection': "keep-alive",
            'cache-control': "no-cache",

        }
        self.lock = threading.Lock()
        self.conn = pymysql.connect(host='localhost', user='root', password='admin', database='data_query', port=3306,charset='utf8')
        self.cur = self.conn.cursor()


    def parse_time(self,link,cookie):
        self.headers['cookie'] = cookie['Cookie']
        res = requests.get(link, headers=self.headers)

        pic_name = f'_{int(time.time())}'
        with open(f'./pic/{pic_name}.jpg','wb') as f:
            f.write(res.content)
        image = Image.open(f"./pic/{pic_name}.jpg")
        #image.show()

        code = pytesseract.image_to_string(image)
        return code

    #数据库持久化
    def save2Mysql(self,data):
        keys = ','.join(data.keys())
        values = ','.join(['%s'] * len(data))

        insert_sql = "insert into flight_info (%s) values (%s)" % (keys, values)
        self.cur.execute(insert_sql, tuple(data.values()))
        self.conn.commit()

    def parse(self):
        self.lock.acquire()
        try:
            start_response = requests.get(self.start_url,headers=self.headers)
            start_response.encoding = "utf-8"
            e = etree.HTML(start_response.text)
            seach_result = e.xpath('//*[@class="searchlist_innerli"]')


            if seach_result:
                name = e.xpath('//*[@class="tit"]/h1/@title')[0].strip()
                log = "{0}航班存在信息...".format(name)
                print(log)
                mylist = e.xpath('//*[@id="list"]/li')
                for selector in mylist:
                    # 获取cookie值
                    cookie = {}
                    cookies = start_response.headers['Set-Cookie']
                    salt = re.findall('salt=(.*?);', cookies)[0]
                    cookie['Cookie'] = f'salt={salt}'

                    # 航班信息
                    flight_info = selector.xpath('div[@class="li_com"]/span[1]/b/a//text()')
                    flight_company = flight_info[0]
                    flight_num = flight_info[1]

                    # 计划起飞
                    FlightDeptimePlan = selector.xpath('div[@class="li_com"]/span[2]/@dplan')[0]

                    # 实际起飞
                    FlightDeptime_img_link = selector.xpath('div[@class="li_com"]/span[6]/img/@src')[0]

                    #计划到达
                    FlightArrtimePlan = selector.xpath('div[@class="li_com"]/span[5]/@aplan')[0]

                    # 实际到达
                    FlightArrtime_img_link = selector.xpath('div[@class="li_com"]/span[3]/img/@src')[0]

                    if FlightDeptime_img_link and FlightArrtime_img_link:
                        FlightDeptime_img_link = urljoin(start_response.url, FlightDeptime_img_link)
                        time1 = self.parse_time(FlightDeptime_img_link,cookie)
                        _time1 = time1.split(":")[0] if time1.split(":")[0][0] else time1.split(":")[0].replace('0', '')

                        FlightArrtime_img_link = urljoin(start_response.url, FlightArrtime_img_link)
                        time2 = self.parse_time(FlightArrtime_img_link,cookie)
                        _time2 = time2.split(":")[0] if time2.split(":")[0][0] else time2.split(":")[0].replace('0','')

                        if _time1 < _time2:
                            FlightDeptime = time1
                            FlightArrtime = time2

                        elif _time1 > _time2:
                            FlightDeptime = time2
                            FlightArrtime = time1


                    elif FlightDeptime_img_link and not FlightArrtime_img_link:
                        FlightDeptime_img_link = urljoin(start_response.url, FlightDeptime_img_link)
                        FlightDeptime = self.parse_time(FlightDeptime_img_link,cookie)
                        FlightArrtime = '暂无信息'

                    elif FlightArrtime_img_link and not FlightDeptime_img_link:
                        FlightArrtime_img_link = urljoin(start_response.url, FlightArrtime_img_link)
                        FlightDeptime = self.parse_time(FlightArrtime_img_link,cookie)
                        FlightArrtime = '暂无信息'

                    else:
                        FlightDeptime = '暂无信息'
                        FlightArrtime = '暂无信息'


                    detailpage_link = selector.xpath('a[@class="searchlist_innerli"]/@href')[0]
                    full_url = urljoin(start_response.url,detailpage_link)

                    response = requests.get(full_url,headers = self.headers)
                    response.encoding = "utf-8"

                    soup = BeautifulSoup(response.text,'lxml')

                    item = {}

                    item["FlightNo"] = self.flightnum

                    item["FlightCompany"] = flight_company

                    info_dep = soup.select('div[class="f_title f_title_a"] h2')[0].text.strip()

                    # 出发地
                    item["FlightDepAirport"] = re.findall(r'[\u4e00-\u9fa5]+',info_dep)[0]

                    # 登机口
                    item["FlightHTerminal"] = re.findall(r'T\d?\w',info_dep)[0] if re.findall(r'T\d?\w',info_dep) else ''

                    #计划起飞
                    item["FlightDeptimePlan"] = FlightDeptimePlan

                    # 实际起飞
                    item["FlightDeptime"] = FlightDeptime

                    info_arr = soup.select('div[class="f_title f_title_c"] h2')[0].text.strip()

                    #到达城市
                    item["FlightArrAirport"] = re.findall(r'[\u4e00-\u9fa5]+',info_arr)[0]

                    # 出机口
                    item["FlightTerminal"] = re.findall(r'T\d?\w',info_arr)[0] if re.findall(r'T\d?\w',info_arr) else ''

                    #计划到达
                    item['FlightArrtimePlan'] = FlightArrtimePlan

                    #实际到达
                    item["FlightArrtime"] = FlightArrtime

                    #机型
                    item["generic"] = soup.select('li[class="mileage"]')[0].text[3:].strip()

                    #机龄
                    item["FlightYear"] = soup.select('li[class="time"] span')[0].text

                    #准点率
                    OntimeRate_link = selector.xpath('div[@class="li_com"]/span[8]/img/@src')[0]
                    OntimeRate_link = urljoin(response.url,OntimeRate_link)
                    item["OntimeRate"] = self.parse_time(OntimeRate_link, cookie)

                    #里程
                    item["distance"] = soup.select('span[class="ti"]')[0].text

                    #飞行时间
                    item["FlightDuration"] = soup.select('span[class="ti"]')[1].text

                    #飞机状态
                    item["FlightState"] = soup.select('div[class="state"]')[0].text.strip()
                    print(item)
                    self.Info.append(item)
                    self.save2Mysql(item)

            else:
                name = e.xpath('//*[@id="byNumInput"]/@value')[0]
                log = "{0}航班不存在信息".format(name)
                print(log)

        except Exception as e:
            print(f'程序出现异常!!!: {e}')

        self.lock.release()


    def MyThread(self):
        thread_list = []
        for i in range(1):
            thread = threading.Thread(target=self.parse)
            thread_list.append(thread)
            thread.start()

        for t in thread_list:
            t.join()
        return self.Info


if __name__ == "__main__":
    flight_num = "SC1155"
    date = '20190723'
    veryaccurate = VeryAccurate(flight_num,date)
    veryaccurate.MyThread()