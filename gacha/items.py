# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GachaItem(scrapy.Item):
    # define the fields for your item here like:
    unames = scrapy.Field()
    visitor = scrapy.Field()
    likes= scrapy.Field()
    concern = scrapy.Field()
    fans = scrapy.Field()
    sex = scrapy.Field()
    address = scrapy.Field()
    img = scrapy.Field()

    def insertdata(self):
        insert_str = """
             INSERT INTO userCACHA(unames,visitor,likes,concern,fans,sex,address,img)
             VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
           """

        parmas = (self['unames'], self['visitor'], self['likes'],
                  self['concern'], self['fans'], self['sex'],self['address'],self['img'])

        return insert_str, parmas


class QuanziItem(scrapy.Item):
    # define the fields for your item here like:
    #获取logo
    logoes = scrapy.Field()
    #用户名
    usersname = scrapy.Field()
    #成员
    member = scrapy.Field()
    #人气
    popularity = scrapy.Field()
    #用户id
    userid = scrapy.Field()
    #内容
    content = scrapy.Field()
    #图片
    img = scrapy.Field()
    #查看
    see = scrapy.Field()
    #评论1
    comments = scrapy.Field()
    #点心
    likes = scrapy.Field()


    def insertdata(self):
        insert_str = """
             INSERT INTO quangacha(logoes,usersname,member,popularity,userid,content,img,see,comments,likes)
             VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
           """

        parmas = (self['logoes'], self['usersname'], self['member'],
                  self['popularity'], self['userid'], self['content'],self['img'],self['see'],self['comments'],self['likes'])

        return insert_str, parmas



class Subject(scrapy.Item):
    title = scrapy.Field()
    intro = scrapy.Field()
    likes = scrapy.Field()
    usname = scrapy.Field()
    xtitle = scrapy.Field()
    img = scrapy.Field()
    xuname = scrapy.Field()
    see = scrapy.Field()

    def insertdata(self):
        insert_str = """
               INSERT INTO sbuject(title,intro,likes,usname,xtitle,img,xuname,see)
               VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
             """

        parmas = (self['title'], self['intro'], self['likes'],
                  self['usname'], self['xtitle'], self['img'], self['xuname'], self['see'])

        return insert_str, parmas



class LaDel(scrapy.Item):
    connent = scrapy.Field()
    img = scrapy.Field()
    def insertdata(self):
        insert_str = """
               INSERT INTO LaDel(connent,img)
               VALUES(%s,%s)
             """

        parmas = (self['connent'], self['img'])

        return insert_str, parmas


