# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class VeryaccurateItem(scrapy.Item):

    # 航空公司
    FlightCompany = scrapy.Field()
    #航班号
    FlightNum = scrapy.Field()
    # 出发城市及机场
    FlightDepAirport = scrapy.Field()
    # 登机口
    FlightHTerminal = scrapy.Field()
    # 计划起飞
    FlightDeptimePlan = scrapy.Field()
    # 实际起飞/预计起飞
    FlightDeptime = scrapy.Field()
    # 降落城市和机场
    FlightArrAirport = scrapy.Field()
    # 降落出口
    FlightTerminal = scrapy.Field()
    # 计划到达
    FlightArrtimePlan = scrapy.Field()
    # 实际到达
    FlightArrtime= scrapy.Field()
    # 机型
    generic = scrapy.Field()
    # 机龄
    FlightYear = scrapy.Field()
    # 历史准点率
    OntimeRate = scrapy.Field()
    # 总里程
    distance = scrapy.Field()
    # 飞行时间
    FlightDuration = scrapy.Field()
    # 飞机状态
    FlightState = scrapy.Field()