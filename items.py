# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity, TakeFirst, Join, Compose, MapCompose

import six


class MemberItem(scrapy.Item):
    username = scrapy.Field()
    full_name = scrapy.Field()
    bio = scrapy.Field()
    location = scrapy.Field()
    images = scrapy.Field()
    devices = scrapy.Field()
    pgp_fingerprint = scrapy.Field()
    twitter = scrapy.Field()
    github = scrapy.Field()
    reddit = scrapy.Field()
    hn = scrapy.Field()
    website = scrapy.Field()
    bitcoin = scrapy.Field()
    zcash = scrapy.Field()
    following = scrapy.Field()
    followers = scrapy.Field()
    image_urls = scrapy.Field()
    email = scrapy.Field()


def absolute_url(url, loader_context):
    return loader_context['response'].urljoin(url)


class MemberLoader(ItemLoader):
    default_item_class = MemberItem
    default_output_processor = TakeFirst()

    website_out = Identity()
    pgp_fingerprint_out = Join(' ')
    full_name_out = Compose(TakeFirst(), six.text_type.strip)
    bio_out = Compose(TakeFirst(), six.text_type.strip)
    location_out = Compose(TakeFirst(), six.text_type.strip)

    image_urls_in = MapCompose(absolute_url)
    image_urls_out = Identity()
