# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import PropertyScraper_mysql_connection as db
class MySQL_OLXOffer_Pipeline(object):
    def process_item(self, item, spider):
        db.create_offer(item)
        return item
