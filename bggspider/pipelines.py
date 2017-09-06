# -*- coding: utf-8 -*-
from scrapy.exceptions import DropItem
import re

DOUBLE_EN_DASH = u'\u2013\u2013'
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

    def process_item(self, item, spider):
        # START CLEANUP
        try:
            fields = [
                'title', 'geek_rating',
                'min_age', 'votes',
                'min_players', 'max_players',
                'weight'
            ]
            for field in fields:
                if field not in item or not field[item]:
                    item[field] = 0
                else:
                    item[field] = item[field].strip()
            item['title'] = item['title'].strip()
            item['geek_rating'] = item['geek_rating'].strip()
            item['min_age'] = item['min_age'].strip()
            item['votes'] = item['votes'].strip()
            item['weight'] = item['weight'].strip()
            if item['time'] == DOUBLE_EN_DASH or item['time'] is None:
                item['time'] = 0
            else:
                item['time'] = item['time'].strip()

            if 'mechanisms' in item:
                item['mechanisms'] = {
                    k.strip() for k in item['mechanisms']
                }
            else:
                item['mechanisms'] = 0
        except AttributeError as err:
            raise DropItem(f'INFO: Dropping {item["title"]}, unhandled field.')
        # END CLEANUP

        # START PROCESSING
        if item['txt_cnt']:
            item['txt_cnt'] = int(re.findall('\d+', item['txt_cnt'])[0])
        else:
            item['txt_cnt'] = 0
        if item['vid_cnt']:
            item['vid_cnt'] = int(re.findall('\d+', item['vid_cnt'])[0])
        else:
            item['vid_cnt'] = 0
        item['review_count'] = item['txt_cnt'] + item['vid_cnt']
        if item['min_age'] == DOUBLE_EN_DASH:
            item['min_age'] = 0
        else:
            item['min_age'] = item['min_age'][:-1]
        if item['geek_rating'] is 'N/A':
            item['geek_rating'] = 0
        if item['votes'] is 'N/A':
            item['votes'] = 0
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