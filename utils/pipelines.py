# -*- coding: utf-8 -*-
# flake8: noqa
# @absurdity 
# pipelines esp. for blox
__author__ = 'nosoyyo'

#############################################################
#·TwitterPipeline·isn't·working·well·due·to·the·wall·u·know·#
#############################################################

# usage
# 
# from web to qiniu:
# q = QiniuPipeline()
# pic_url = 'http://some.pic.url'
# ret = q.upload(pic_url)
# 
# from qiniu to distribution:
# q = QiniuPipeline()
# downloadable_file_url = q.getFile(key)

import pymongo

import ezcf
import conf

# ==================
# MongoDB quickstart
# ==================

class Singleton(object):
    _instance = None
    def __new__(cls, dbname, usr, pwd, *args, **kw):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kw)  
        return cls._instance 

class MongoDBPipeline(Singleton):

    def __init__(self, dbname, usr, pwd, conf=conf):

        self.client = pymongo.MongoClient(
            conf.MongoDBServer,
            conf.MongoDBPort,
            username=usr,
            password=pwd,
            ssl=conf.MongoDBSSL,
            #ssl_certfile=conf.MongoDBSSL_CERTFILE,
            #ssl_keyfile=conf.MongoDBSSL_KEYFILE,
        )
        self.db = self.client.get_database(dbname)
        self.auth = self.db.authenticate(usr, pwd)
        self.col = self.db.get_collection(conf.MongoDBInitCol)

    def setDB(self, dbname):
        self.db = self.client.get_database(dbname)
        return self

    def setCol(self, dbname, colname):
        self.db = self.client.get_database(dbname)
        self.col = self.db.get_collection(colname)
        return self

    def ls(self):
        return self.db.list_collection_names()


# ===============
# wxpy quickstart
# ===============

class WxpyPipeline():

    def __init__(self, cache_path=True, console_qr=True,):
        '''
            'from wxpy import *'' only allowed at module level, so
        '''
        import sys
        import logging

        from wxpy.api.bot import Bot
        from wxpy.api.chats import Chat, Chats, Friend, Group, Groups, MP, Member, User
        from wxpy.api.consts import ATTACHMENT, CARD, FRIENDS, MAP, NOTE, PICTURE, RECORDING, SHARING, SYSTEM, TEXT, VIDEO
        from wxpy.api.consts import FEMALE, MALE
        from wxpy.api.messages import Article, Message, Messages, SentMessage
        from wxpy.exceptions import ResponseError
        from wxpy.ext import Tuling, WeChatLoggingHandler, XiaoI, get_wechat_logger, sync_message_in_groups
        from wxpy.utils import BaseRequest, detect_freq_limit, dont_raise_response_error, embed, ensure_one, mutual_friends
        
        self.bot = Bot(conf.cache_path, conf.console_qr)
        self.bot.enable_puid()
        return 

    m = MongoDBPipeline(conf.WxpyDBName, conf.WxpyDBUser, conf.WxpyDBPwd)
    puid_col = m.setCol(conf.WxpyDBName, 'profile').col.wx.puid

    # get staff list


# ================
# Qiniu quickstart
# ================

class QiniuPipeline():

    # import
    from qiniu import Auth, BucketManager, put_file, etag, urlsafe_base64_encode
    import qiniu.config

    def __init__(self, dbname, usr, pwd):
        self.m = MongoDBPipeline(dbname, usr, pwd)
        self.m_auth = self.m.auth
        self.keys = self.m.setCol(conf.QiniuDBUser, conf.QiniuProfileCol).col.find()[0].keys
        self.access_key = self.keys.access_key
        self.secret_key = self.keys.secret_key
    
        # 构建鉴权对象
        self.auth = self.Auth(self.access_key, self.secret_key)
    
        # bucket
        self.bucket = BucketManager(self.auth)

    #要上传的空间
    bucket_name = conf.BucketName

    #上传到七牛后保存的文件名前缀
    #prefix = 'tommy'

    def upload(self, pic_url):
        bucket_name = self.bucket_name
        key = pic_url.split('/')[-1]
        token = self.auth.upload_token(bucket_name, key, 0)
        ret = self.bucket.fetch(pic_url, bucket_name, key)
        return ret

    def getFile(self, key):
        url = self.auth.private_download_url(conf.QINIU_PRIVATE + key)
        return url

    def ls(self):
        l = self.bucket.list(self.bucket_name)[0].items
        return l

    def count(self):
        c = len(self.bucket.list(self.bucket_name)[0].items)
        return c

# ==================
# Twitter quickstart
# ==================

class TwitterPipeline():

    def __init__(self, dbname, username, password):

        # import
        import tweepy

        # init m
        self.m = MongoDBPipeline(dbname, username, password)
        self.m_auth = self.m.auth
        self.keys = self.m.setCol(conf.TWITTER_USERNAME, conf.TWITTER_PROFILE).col.find()[0].keys

        # get keys
        consumer_key = self.keys.consumer_key
        consumer_secret = self.keys.consumer_secret
        access_token = self.keys.access_token
        access_token_secret = self.keys.access_token_secret

        # auth and get APIs
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret) 
        auth.set_access_token(self.access_token, self.access_token_secret)
        api = tweepy.API(self.auth)