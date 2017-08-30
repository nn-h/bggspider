# -*- coding: utf-8 -*-
from scrapy.exceptions import DropItem
import re
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

''' BoardgamePipeline filters the received selectively,
    if a boardgame does not have a Geek Rating. It can generally
    imply that the boardgame doesn\'t have a userbase following on the
    site and can be assumed that there are not enough people who have
    reviewed the game or even rated on it for that matter.
'''


class BoardgamePipeline(object):

    def opens_spider(self, spider):
        self.file = open('bgg.json', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        # START CLEANUP
        try:
            item['title'] = item['title'].strip()

            if item['min_players'] is None:
                item['min_players'] = 0
            else:
                item['min_players'] = item['min_players'].strip()
            if item['max_players'] is None:
                item['max_players'] = 0
            else:
                item['max_players'] = item['max_players'].strip()
            if item['time'] == u"\u2013":
                item['time'] = 0
            else:
                item['time'] = item['time'].strip()
            
            item['weight'] = item['weight'].strip()
            item['min_age'] = item['min_age'].strip()
            item['mechanisms'] = {
                k.strip() for k in item['mechanisms']
            }
        except AttributeError as err:
            raise DropItem(f'BG: {item["title"]}, doesn\'t have enough features {item}')
            print(err)

        # END CLEANUP

        # START PROCESSING
        txt_cnt = re.search('\d+', item['txt_cnt'])
        vid_cnt = re.search('\d+', item['vid_cnt'])
        if txt_cnt is not None:
            txt_cnt = int(re.findall('\d+', item['txt_cnt'])[0])
        else:
            txt_cnt = 0
        if vid_cnt is not None:
            vid_cnt = int(re.findall('\d+', item['vid_cnt'])[0])
        else:
            vid_cnt = 0
        item['review_count'] = txt_cnt + vid_cnt
        if re.match('-', item['min_age']):
                item['min_age'] = 0
        else:
            # cleanup the '+'
            item['min_age'] = item['min_age'][:-1]
        # END PROCESSING

        # START FILTERING
        if item['geek_rating'] is not 'N/A':
            fields = [
                'min_age', 'time', 'votes', 'min_players', 'max_players'
            ]
            float_fields = [
                'weight', 'avg_rating', 'geek_rating'
            ]
            for field in fields:
                item[field] = int(item[field])
            for field in float_fields:
                item[field] = float(item[field])

            # remove unwanted fields
            item.pop('txt_cnt', None)
            item.pop('vid_cnt', None)
            print(f'PROCESSED: {item["bg_id"]}, {item["title"]}')
            return item
        else:
            raise DropItem(f'BG: {item["title"]}, doesn\'t have enough reviews {item["review_count"]}')
        # END FILTERING