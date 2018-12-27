# -*- coding: utf-8 -*-

# Scrapy settings for keybase project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'keybase'

SPIDER_MODULES = ['keybase.spiders']
NEWSPIDER_MODULE = 'keybase.spiders'

ROBOTSTXT_OBEY = True

ITEM_PIPELINES = {
    'scrapy.pipelines.images.ImagesPipeline': 1,
    'keybase.pipelines.KeybasePipeline': 2,
}
IMAGES_STORE = 'images'
