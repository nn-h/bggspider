from scrapy_splash import SplashRequest
from scrapy import Spider
from .. import selector_paths
from ..items import Boardgame

BASE_URI = "https://boardgamegeek.com"
LIST_URL = BASE_URI + "/browse/boardgame"
CREDITS_URI = '/credits'


class BGGSpider(Spider):
    name = 'bgg_spider'
    allowed_domains = ['boardgamegeek.com']
    start_urls = [
        LIST_URL
    ]

    def parse(self, response):
        for row_ in response.xpath('.//tr[@id="row_"]'):
            bg = Boardgame()
            bg['title'] = row_.xpath(
                selector_paths.SEL_TITLE).extract_first()
            bg['geek_rating'], bg['avg_rating'], bg['votes'] = [x for x in row_.xpath(selector_paths.SEL_METRICS).extract()]
            if 'N/A' in bg['geek_rating'] and 'N/A' in bg['avg_rating']:
                print('INFO: Not enough information dropping BG.')
                yield
            bg_link = BASE_URI + row_.xpath(
                selector_paths.SEL_LINK).extract_first()
            bg['bg_id'] = bg_link.split('/')[4]
            yield SplashRequest(
                url=bg_link,
                callback=self.parse_boardgame,
                meta={'bg': bg, 'bg_link': bg_link}
            )

        next_page = response.xpath(selector_paths.SEL_NEXT_PG).extract_first()
        next_page_url = response.urljoin(next_page)
        yield SplashRequest(
            url=next_page_url,
            callback=self.parse
        )

    def parse_boardgame(self, response):
        bg = response.meta['bg']
        # bg_link = response.meta['bg_link']

        # get min/max players
        bg['min_players'] = response.xpath(
            selector_paths.SEL_MIN_PLAYERS).extract_first()
        bg['max_players'] = response.xpath(
                selector_paths.SEL_MAX_PLAYERS).extract_first()

        # check for min/max time
        bg['time'] = response.xpath(
            selector_paths.SEL_MAX_TIME).extract_first()
        if bg['time'] is None:  # no max time, get min.
            bg['time'] = response.xpath(selector_paths.SEL_MIN_TIME).extract_first()

        bg['weight'] = response.xpath(
            selector_paths.SEL_WEIGHT).extract_first()
        bg['min_age'] = response.xpath(
            selector_paths.SEL_MIN_AGE).extract_first()
        # some pages do not contain reviews, do some exception work.
        bg['txt_cnt'] = response.xpath(
            selector_paths.SEL_TXT_REVIEWS).extract_first()
        bg['vid_cnt'] = response.xpath(
            selector_paths.SEL_VID_REVIEWS).extract_first()
        # credits_link = bg_link + CREDITS_URI
        bg['mechanisms'] = {
            k
            for
            k in response.xpath(
                selector_paths.SEL_MECHANISMS_ALT).extract()
        }
        # yield SplashRequest(
        #     credits_link,
        #     callback=self.parse_credits,
        #     meta={'bg': bg}
        # )
        yield bg

    def parse_credits(self, response):
        bg = response.meta['bg']
        bg['mechanisms'] = {
            k
            for
            k in response.xpath(
                selector_paths.SEL_MECHANISMS).extract()
        }
        if 'mechanisms' not in bg:
            # try the old markup method
            bg['mechanisms'] = {
                k
                for
                k in response.xpath(
                    selector_paths.SEL_MECHANISIMS_ALT).extract()
            }
        yield bg
