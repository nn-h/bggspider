# -*- coding: utf-8 -*-
from scrapy.exceptions import DropItem
import re
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class BoardgamePipeline(object):

    def opens_spider(self, spider):
        self.file = open('bgg.json', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        txt_rev = re.findall('\d+', item['txt_cnt'])[0]
        vid_rev = re.findall('\d+', item['vid_cnt'])[0]
        item['review_count'] = int(txt_rev) + int(vid_rev)
        if item['review_count'] > 10:
            fields = [
                'min_age', 'time', 'votes', 'min_players', 'max_players'
            ]
            float_fields = [
                'weight', 'avg_rating', 'geek_rating'
            ]
            # cleanup the '+'
            item['min_age'] = item['min_age'][:-1]
            for field in fields:
                item[field] = int(item[field])
            for field in float_fields:
                item[field] = float(item[field])

            # remove unwanted fields
            item.pop('txt_cnt', None)
            item.pop('vid_cnt', None)
            return item
        else:
            raise DropItem(f'BG: {item["title"]}, doesn\'t have enough reviews {item["review_count"]}')
