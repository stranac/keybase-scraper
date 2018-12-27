import itertools
import json
from string import ascii_lowercase

import scrapy
# XXX: rewritten to use autocomplete/search instead of following links
# from scrapy.spiders import Rule, CrawlSpider
# from scrapy.linkextractors import LinkExtractor
from w3lib.url import url_query_parameter

from keybase.items import MemberLoader

SEARCH_URL = 'https://keybase.io/_/api/1.0/user/autocomplete.json?q={}&num_wanted=100'


class KeybaseMembersSpider(scrapy.Spider):
    name = 'members'
    # XXX: rewritten to use autocomplete/search instead of following links
    start_urls = [
        SEARCH_URL.format(''.join(t))
        for n in range(1, 4)
        for t in itertools.product(ascii_lowercase, repeat=n)
    ]

    # rules = [
    #     Rule(
    #         LinkExtractor(restrict_css=['.username']),
    #         callback='parse_profile',
    #         follow=True,
    #     ),
    # ]

    def parse(self, response):
        data = json.loads(response.text)
        usernames = [user['components']['username']['val'] for user in data['completions']]
        for username in usernames:
            yield scrapy.Request(
                url='https://keybase.io/{}'.format(username),
                callback=self.parse_profile,
            )
        if len(usernames) == 100:
            q = url_query_parameter(response.url, 'q')
            for c in ascii_lowercase:
                yield scrapy.Request(url=SEARCH_URL.format(q + c))

    def _icon(self, title):
        return '.icon-kb-iconfont-identity-{}'.format(title)

    def _followers_request(self, reverse, uid, last_uid, item):
        return scrapy.FormRequest(
            url='https://keybase.io/_/api/1.0/user/load_more_followers.json',
            method='GET',
            formdata={
                'reverse': '1' if reverse else '0',
                'uid': uid,
                'last_uid': '{:0>32}'.format(last_uid),
                'num_wanted': '100',
            },
            callback=self.parse_following if reverse else self.parse_followers,
            meta={'item': item, 'uid': uid},
        )

    def parse_profile(self, response):
        loader = MemberLoader(response=response)
        loader.add_css('username', 'div.username::text')
        loader.add_xpath('full_name', '//div[@class="full-name "]/text()[normalize-space()]')
        loader.add_css('bio', '.bio::text')
        loader.add_css('location', '.location::text')
        loader.add_css('image_urls', '.picture img::attr(src)')

        id_loader = loader.nested_xpath('//div[@class="identity-table"][1]')
        id_loader.add_css('devices', self._icon('devices') + ' + a::text')
        id_loader.add_css('pgp_fingerprint', '.pgp-fingerprint > span::text')
        id_loader.add_css('twitter', self._icon('twitter') + ' + a::attr(href)')
        id_loader.add_css('github', self._icon('github') + ' + a::attr(href)')
        id_loader.add_css('reddit', self._icon('reddit') + ' + a::attr(href)')
        id_loader.add_css('hn', self._icon('hn') + ' + a::attr(href)')
        id_loader.add_css('website', self._icon('website') + ' + a::attr(href)')
        id_loader.add_xpath('bitcoin', '//a[@data-type="bitcoin"]/@data-address')
        id_loader.add_xpath('zcash', '//a[@data-type="zcash.t"]/@data-address')

        item = loader.load_item()

        uid = response.css('.profile-heading::attr(data-uid)').get()
        yield self._followers_request(
            reverse=True,
            uid=uid,
            last_uid='0',
            item=item
        )

    def _get_selector(self, response):
        data = json.loads(response.text)
        if 'snippet' not in data:
            return
        return scrapy.Selector(text=data['snippet'])

    def parse_following(self, response):
        item = response.meta['item']
        sel = self._get_selector(response)
        following = sel.css('.username::text').getall()

        if following:
            item.setdefault('following', []).extend(following)
            # XXX: rewritten to use autocomplete/search instead of following links
            # for username in following:
            #     yield scrapy.Request(
            #         url='https://keybase.io/{}'.format(username),
            #         callback=self.parse_profile,
            #     )
            last_uid = sel.css('tr::attr(data-uid)').getall()[-1]
            yield self._followers_request(
                reverse=True,
                uid=response.meta['uid'],
                last_uid=last_uid,
                item=item,
            )
        else:
            yield self._followers_request(
                reverse=False,
                uid=response.meta['uid'],
                last_uid='0',
                item=item,
            )

    def parse_followers(self, response):
        item = response.meta['item']
        sel = self._get_selector(response)
        followers = sel.css('.username::text').getall()

        if followers:
            item.setdefault('followers', []).extend(followers)
            # XXX: rewritten to use autocomplete/search instead of following links
            # for username in followers:
            #     yield scrapy.Request(
            #         url='https://keybase.io/{}'.format(username),
            #         callback=self.parse_profile,
            #     )
            last_uid = sel.css('tr::attr(data-uid)').getall()[-1]
            yield self._followers_request(
                reverse=False,
                uid=response.meta['uid'],
                last_uid=last_uid,
                item=item,
            )
        else:
            yield item
