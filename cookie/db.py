# -*- coding: UTF-8 -*-

import pymongo
from datetime import datetime, timedelta

class InitMessages(object):
    def __init__(self):
        host = '139.199.59.214'
        self.db = pymongo.MongoClient(host, 8777)['pricedb']
        self.tencentAccount = self.db['tencentAccount']
        self.limit = 14
        self.timedelta = datetime.utcnow() - timedelta(hours=25)

    def getAccounts(self):
        cursor = self.tencentAccount.find({'enabled': 1, 'lastUseDate': {'$lte': self.timedelta}})\
                 .sort([('lastUseDate', 1)])
        list = []
        for item in cursor:
            list.append(item)
        print('total available qq count: %s' % (len(list)))
        return list

    def updateAccount(self, qq):
        result = self.tencentAccount.update({'qq': qq}, {'$set': {'lastUseDate': datetime.utcnow()}})
        print(result)

    def updateAccounts(self, qqs):
        result = self.tencentAccount.update({'qq': {'$in': qqs}}, {'$set': {'lastUseDate': datetime.utcnow()}}, multi=True)
        print(result)

    def updateFailedAccount(self, qq):
        result = self.tencentAccount.update({'qq': qq}, {'$set': {'enabled': 0, 'lastUseDate': datetime.utcnow()}})
        print(result)
myMess = InitMessages()
myMess.getAccounts()

