# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from twisted.enterprise import adbapi
import pymysql
class GachaPipeline(object):
    def __init__(self,dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls,settings):
        parmas = {
            'host': settings['MYSQL_HOST'],
            'user': settings['MYSQL_USER'],
            'passwd':settings['MYSQL_PASSWD'],
            'db':settings['MYSQL_DB'],
            'port':3306,
            'charset':'utf8',
        }
        #使用ConnectinPool,,起始最后1返回一个ThreadPoll
        dbpool = adbapi.ConnectionPool('pymysql',**parmas)

        return cls(dbpool)


    def process_item(self,item,spider):
        #这里去调用1任务分配的方法
        query = self.dbpool.runInteraction(self.insert_data_todb,item,spider)
        query.addErrback(self.handle_error, item)

    def insert_data_todb(self, cursor, item, spider):
        insert_str, parmas = item.insertdata()
        cursor.execute(insert_str, parmas)
        print('插入成功')

    def handle_error(self, failure, item):
        print(failure)
        print('插入错误')
        # 在这里执行你想要的操作

    def close_spider(self, spider):
        pass