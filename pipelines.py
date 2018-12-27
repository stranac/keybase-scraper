# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re

import scrapy
from twisted.internet import protocol, reactor, defer


GPG_PATH = r'C:\Program Files (x86)\Cmder\vendor\git-for-windows\usr\bin\gpg.exe'
PGP_URL = 'https://keybase.io/{}/pgp_keys.asc'


class GPGProcessProtocol(protocol.ProcessProtocol):
    def __init__(self, key):
        self.key = key
        self.dfd = defer.Deferred()

    def connectionMade(self):
        self.transport.write(self.key)
        self.transport.closeStdin()

    def outReceived(self, data):
        self.transport.loseConnection()
        self.dfd.callback(data)


def extract_email(data):
    return re.search('<([^>]+)>', data.decode('utf-8')).group(1)


class KeybasePipeline(object):
    @defer.inlineCallbacks
    def process_item(self, item, spider):
        if 'pgp_fingerprint' in item:
            request = scrapy.Request(PGP_URL.format(item['username']))
            response = yield spider.crawler.engine.download(request, spider)

            gpg_process = GPGProcessProtocol(response.body)
            reactor.spawnProcess(gpg_process, GPG_PATH, ['gpg', '--list-packets'])
            data = yield gpg_process.dfd

            item['email'] = extract_email(data)
        defer.returnValue(item)
