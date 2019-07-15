# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json

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

