# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json

import pymysql
import requests
import scrapy
import pytesseract
from PIL import Image


class FilePipeline(object):
    def __init__(self):
        self.file = open('flight_info.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        # 这里需要把item转换字典
        item_json = json.dumps(dict(item), ensure_ascii=False)
        self.file.write(item_json + '\n')
        return item


    def close_spider(self, spider):
        self.file.close()

#插入数据库
class MysqlPipeline(object):
    def __init__(self,host,port,user,password,database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

    @classmethod
    def from_crawler(cls,crawler):
        return cls(
            host = crawler.settings.get('MYSQL_HOST'),
            port=crawler.settings.get('MYSQL_PORT'),
            user=crawler.settings.get('MYSQL_USER'),
            password=crawler.settings.get('MYSQL_PASSWORD'),
            database=crawler.settings.get('MYSQL_DBNAME')
        )

    def open_spider(self, spider):
        # 连接数据库
        self.conn = pymysql.connect(self.host,self.user,self.password,self.database,self.port,charset='utf8')
        self.cur = self.conn.cursor()  # 游标

    def process_item(self, item, spider):
        data = dict(item)
        if len(data) ==1:
            pass
        else:
            keys = ','.join(data.keys())
            values = ','.join(['%s'] * len(data))

            insert_sql = "insert into flight_info(%s) values (%s)" % (keys,values)
            self.cur.execute(insert_sql,tuple(data.values()))
            self.conn.commit()

        return item

    def close_spider(self, spider):
        self.cur.close()  # 关闭游标
        self.conn.close()  # 关闭数据库
