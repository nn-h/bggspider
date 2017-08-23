# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
from scrapy import Field, Item


class Boardgame(Item):
    bg_id = Field()
    title = Field()
    geek_rating = Field()
    avg_rating = Field()
    votes = Field()
    time = Field()
    min_age = Field()
    max_players = Field()
    min_players = Field()
    weight = Field()
    mechanisms = Field()
    txt_cnt = Field()
    vid_cnt = Field()
    review_count = Field()
