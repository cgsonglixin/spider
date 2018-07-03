# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import json
from gacha.items import *
from lxml  import etree
import re
class GetgachaSpider(CrawlSpider):

    name = 'getgacha'
    allowed_domains = ['gacha.163.com']
    start_urls = ['http://gacha.163.com/']

    rules = (
        Rule(LinkExtractor(allow=r'.*?/discover/pic$',restrict_xpaths='//div[@class="gradient-mask"]'), callback='parse_discover', follow=True),
        Rule(LinkExtractor(allow=r'.*?type=1', restrict_xpaths='//div[@class="circle-about f-cb"]'), callback='parse_quanzi',
             follow=True),
        # 专题
        Rule(LinkExtractor(allow=r'', restrict_xpaths='//li[@class="f-fl first j-hot-collect-nav j-nav-tag-change  "]'),
             callback='parse_subject',
             follow=True),



    )
    # def __init__(self):
    #     self.pagenum = 1


    def parse_item(self, response):

        pass


    def parse_discover(self,response):
        # print('热门')
        # print(response.url)
        url = 'http://gacha.163.com/api/v1/insert/getList?newest=0'
        yield scrapy.Request(url,self.parse_discover_json)

    #获取插画中的新作
    def parse_discover_json(self,response):
        parses = json.loads(response.text)
        for items in parses['result']['list']:

            name = items['name']
            id = items['postId']
            userid = items['userid']
            imgurl = items['headpic']
            imgurl = 'http://gacha.nosdn.127.net/%s?imageView&type=jpg&enlarge=1&quality=100&axis=0&thumbnail=0x400' %imgurl
            url = 'http://gacha.163.com/api/v1/insert/getList?newest=0&endId=%s'%parses['result']['list'][-1]['id']
            userurl = 'http://gacha.163.com/homepage/%s/index' %userid
            contenturl = 'http://gacha.163.com/detail/post/%s' % id
            yield scrapy.Request(contenturl, callback=self.parse_content)
            yield scrapy.Request(userurl,callback=self.parse_user)
            yield scrapy.Request(url,callback=self.parse_discover_json)

            # print(name,imgurl,userid,imgurl,contenturl)


    def parse_content(self,response):
        item = LaDel()
        item['connent'] = ''.join(response.xpath('//div[@class="rich-txt "]/text()').re('\S+'))
        item['img'] = ''.join(response.xpath('//div[@class="pic dtimg-wrap j-dtimg-wrap  j-track-event-Node"]//img/@src').extract())
        if len(item['connent']) == 0:
            item['connent'] = "空"
            item['img'] = "空"
        yield item
    #提取用户页面
    def parse_user(self,response):
        item = GachaItem()
        #提取用户名
        item['unames'] = response.xpath('//h3[@class="user-name"]/text()').re('\S+')[0]
        item['visitor'] = response.xpath('//span[@class="num j-show-visitor"]/text()').re('\d+')[0]
        item['likes'] = response.xpath('//span[@class="num j-show-visitor"]/text()').re('\d+')[0]
        item['concern'] = response.xpath('//div[@class="content f-cb art-mes"]/div[3]/a/text()').re('\d')[0]
        item['fans'] = response.xpath('//div[@class="content f-cb art-mes"]/div[4]/a/span/text()').re('\d')[0]
        item['sex'] = response.xpath('//p[@class="content f-toe"]/span[4]/text()').extract_first('空')
        item['address'] = response.xpath('//p[@class="content f-toe"]/span[3]/text()').extract_first('空')
        item['img'] = ','.join(response.xpath('//img[@class="scale-pic u-rds-4"]/@src').extract())
        if len(item['img']) > 200:
            item['img'] = item['img'][0:150]

        # print(item['address'],item['sex'])
        yield item


    def parse_quanzi(self,response):
        # print('开始爬去圈子')
        pageurl = 'http://gacha.163.com/api/v1/circles?pageNum=1'
        yield scrapy.Request(pageurl,callback=self.parse_pagenum)

    #爬取全部圈子
    def parse_pagenum(self,response):
        pagexml = json.loads(response.text)
        if pagexml['result']['circleHtml']:
            pnum = re.findall(re.compile('.*?\\=(\d+)'),response.url)[0]
            # print(pnum)
            pnum = int(pnum) + 1
            pageurl = 'http://gacha.163.com/api/v1/circles?pageNum=%s' %pnum
            pagehtml = etree.HTML(pagexml['result']['circleHtml'])
            #获取圈子id
            items  = pagehtml.xpath('//li[@class="circle-item f-fl"]/@data-id')
            for pageitems in items:
                circleurl = 'http://gacha.163.com/circle/%s?pageNum=1'%pageitems
                # print(circleurl)
                #通过圈子id拼接链接，并请求
                # print(circleurl)
                yield scrapy.Request(circleurl,callback=self.parse_circle)
                #获取下一页
                yield scrapy.Request(pageurl,callback=self.parse_pagenum)

        else:
            print(response.url[-1])


    #解析圈子内容
    def parse_circle(self,response):
        item = QuanziItem()
        prepage = int(re.findall(re.compile('.*?\\=(\d+)'),response.url)[0])
        # print(prepage)
        # 获取logo
        # print(response.url)
        item['logoes'] = response.xpath('//img[@class="circle-banner"]/@src').extract()[0]
        # 获取成员
        item['member'] = response.xpath('//div[@class="member-count j-cird-memcount"]/text()').extract_first()
        # #获取人气数据
        item['popularity'] = response.xpath('//div[@class="post-count"]/text()').extract_first()
        html = etree.HTML(response.text)
        text = html.xpath('//div[@class="m-post-item j-m-post-item f-wwb  "]')
        for ites in text:
            # 获取用户id
            item['userid'] = ites.xpath('.//span[@class="j-user-about f-toe"]/@data-id')[0]
            # print(item['userid'])
            # 用户名字
            item['usersname'] = ites.xpath('.//span[@class="j-user-about f-toe"]/text()')[0]
            # print()
            # 获取内容
            item['content'] = ''.join(ites.xpath('.//div[@class="min-cont-c"]/text()')).replace('\n', '').replace('\xa0',
                                                                                                          '').replace(
                ' ', '')
            item['img'] = ''.join(html.xpath('.//img[@class="f-fl"]/@src'))
            # 获取查看
            item['see'] = ''.join(ites.xpath('.//li[@class="action f-cb f-fl"]/text()')).replace(' ', '').replace('\n',
                                                                                                          '').replace(
                '浏览', '').replace('\xa0','')
            # 获取评论参数
            comments = ites.xpath('.//div[@class="m-post-item j-m-post-item f-wwb  "]/@data-id')
            item['likes'] = ''.join(ites.xpath('.//span[@class="txt f-fl j-count support-txt"]/text()'))
            # 拼接评论的url
            item['comments'] = 'kong'
            commenturl = 'http://gacha.163.com/api/v1/post/%s/commentList?pageCount=50' % comments
            yield item
            # yield scrapy.Request(commenturl, callback=self.parse_comments,meta={'item':item})


        button = response.xpath('//button[@class="but jointo j-joinin-circle"]/@data-id').extract_first()
        id = response.xpath('//div[@class="m-post-item j-m-post-item f-wwb  "][last()]/@data-id').extract_first()
        prepage = prepage + 1
        if len(button) > 0:
            newurl = 'http://gacha.163.com/circle/%s?pageNum=%s'%(button,prepage)
            yield scrapy.Request(newurl,callback=self.parse_circle)
            newurljson = 'http://gacha.163.com/api/v1/post/getList/circleDetail?circleId=%s&postType=all&endId=%s&prePage=%s&page=%s'%(button,id,prepage,prepage)
            # print(newurljson)
            #
            # yield scrapy.Request(newurljson,callback=self.parse_circle_content,meta={'logo':item['logoes'],'member':item['member'],'popularity':item['popularity']})


     #解析圈子全部话题
    def parse_circle_content(self,response):
        item = QuanziItem()
        item['popularity'] = response.meta['popularity']
        item['logoes'] = response.meta['logo']
        item['member']= response.meta['member']
        # print('开始分析页数')
        # print(response.url)
        # print(response.url)
        # button = response.meta['button']
        # ids = response.meta['id']
        # print(button)
        text = json.loads(response.text)
        htmls = etree.HTML(text['result']['postList'])
        if htmls:
            for html in htmls.xpath('//div[@class="j-m-post-item-wrap m-post-item-wrap   u-rds-4"]'):
                item['userid'] = html.xpath('.//span[@class="j-user-about f-toe"]/@data-id')[0]
                # 用户名字
                item['usersname'] = html.xpath('.//span[@class="j-user-about f-toe"]/text()')[0]
                # 获取内容
                item['content'] = ''.join(html.xpath('.//div[@class="min-cont-c"]/text()')).replace('\n', '').replace(
                    '\xa0',
                    '').replace(
                    ' ', '')
                item['img'] = ''.join(html.xpath('.//img[@class="f-fl"]/@src'))
                # 获取查看
                item['see'] = ''.join(html.xpath('.//li[@class="action f-cb f-fl"]/text()')).replace(' ', '').replace(
                    '\n',
                    '').replace(
                    '浏览', '').replace('\xa0','')
                # 获取评论参数
                comments = html.xpath('.//div[@class="m-post-item j-m-post-item f-wwb  "]/@data-id')
                item['likes'] = ''.join(html.xpath('.//span[@class="txt f-fl j-count support-txt"]/text()'))
                # 拼接评论的url
                commenturl = 'http://gacha.163.com/api/v1/post/%s/commentList?pageCount=50' % comments

                yield scrapy.Request(commenturl, callback=self.parse_comments, meta={'item': item})
                # id = response.xpath('//div[@class="m-post-item j-m-post-item f-wwb  "]/@data-id').extract()[0]







    def parse_comments(self,response):
        item = response.meta['item']
        # print('解析评论')

        comment = json.loads(response.text)
        if len(comment['result']['commentList']) > 0:
            a = []
            for comments in comment['result']['commentList']:
                a.append(comments['cont'])
            item['comments'] = ','.join(a)
            yield item


        else:
            item['comments'] = '没有评论'
            yield item


    #解析推荐
    def parse_subject(self,response):
        #获取最后一个id作为链接的参数
        s_id = response.xpath('//a[@class="j-track-event-Node"]//div[@class="col-item  first f-fl"]/@data-cid').extract()
        # print(s_id)
        s_url = 'http://gacha.163.com/api/v1/collectchannel/list?pageCount=20&pageNum=1&subType=0&colType=0&lastId=%s&prePage=1'%s_id[-1]
        yield scrapy.Request(s_url,callback=self.parse_subjson)


    def parse_subjson(self,response):
        sub_json = json.loads(response.text)
        sub_html = etree.HTML(sub_json['result']['strHtml'])
        for sub_item in sub_html:
            #获取内部链接
            sub_href = sub_item.xpath('//a[@class="j-track-event-Node"]/@href')
            #循环sub-href
            for sub_hrefs in sub_href:
                nsub_url = 'http://gacha.163.com'+sub_hrefs
                # print(nsub_url)
                yield scrapy.Request(nsub_url,callback=self.parse_subject_connet)

            #获取所有专题
            s_id = sub_item.xpath('//div[@class="col-item   f-fl"]/@data-cid')

            s_url = 'http://gacha.163.com/api/v1/collectchannel/list?pageCount=20&pageNum=1&subType=0&colType=0&lastId=%s&prePage=1' % s_id[-1]
            yield scrapy.Request(s_url, callback=self.parse_subjson)





    def parse_subject_connet(self,response):
        item = Subject()
        #获取标题
        item['title'] = ''.join(response.xpath('//div[@class="f-fl fav-left"]//div[@class="fav-name j-fav-name f-toe"]/text()').extract())
        # if len(item['title']) == 0 ；

        #获取简介
        item['intro'] = response.xpath('//div[@class="fav-desc j-fav-desc"]/text()').extract_first('空')
        if item['intro'] == '空':
            print(response.url,'kong')
        #点心
        item['likes'] = response.xpath('//div[@class="support-num"]/text()').extract_first()
        #用户名
        item['usname'] = response.xpath('//span[@class="userInfo-name f-toe"]/text()').extract_first()
        #小标
        item['xtitle'] = '--'.join(response.xpath('//div[@class="collect-reason"]//text()').extract()).replace('\n','').replace(' ','')[2:]
        #获取图片第一种类型
        itemimg1 = response.xpath('//div[@class="thumbnail-item thumbnail-item-all j-fav-detl-pic-i"]/img/@src').extract()
        # #获取图片第二种类型
        itemimg2 = response.xpath('//div[@class="thumbnail-item j-fav-detl-pic-i thumbnail-item-top"]/img/@src').extract()
        #合并
        item['img'] = '--'.join(itemimg1 + itemimg2)[2:]
        #小用户
        item['xuname'] = '--'.join(response.xpath('//div[@class="username j-user-about f-fl"]/text()').extract())[2:]
        #浏览
        item['see'] = '--'.join(response.xpath('//li[@class="action f-cb f-fl"]/text()').extract()).replace('\n','').replace(' ','')[2:]
        # print(item['title'],item['intro'],item['likes'],item['usname'],item['xtitle'],item['img'],item['xuname'],item['see'])

        yield item




    def parse_label(self,response):
        item = LaDel()
        item['title']=response.xpath('//a[@class="name f-fwb f-toe"]/text()').extract_first('未知')
        item['member'] = response.xpath('//div[@class="item f-fl first"]/span/text()').extract_first('未知')
        item['likes'] = response.xpath('//div[@class="item f-fl last"]/span/text()').extract_first('未知')
        l_html = etree.HTML(response.text)
        l_text = l_html.xpath('//div[@class="m-post-item j-m-post-item f-wwb  "]')
        for l_item in l_text:
            unames = ''.join(l_item.xpath('.//span[@class="j-user-about f-toe"]/text()')).replace('\n','').replace(' ','' )
            l_content = '.'.join(l_item.xpath('.//div[@class="min-cont-c"]//text()')).replace('\n','').replace(' ','' )
            img  =  ''.join(l_item.xpath('.//div[@class="media-thumb-box j-media-thumb-box"]//img/@src'))
            if len(unames)== 0:
                unames = ''.join(l_item.xpath('.//h3[@class="title f-toe j-track-event-Node"]/text()')).replace('\n','').replace(' ','' )
            if len(l_content) == 0:
                l_content = ''.join(l_item.xpath('.//div[@class="vedio-title f-toe"]/text()')).replace('\n','').replace(' ','' )
            if len(img) == 0:
                img = '无图片'
            print(unames,l_content,img)
            print(response.url)
        # print(item['title'],item['member'],item['likes'])


