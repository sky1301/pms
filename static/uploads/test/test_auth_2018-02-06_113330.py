#!/usr/bin/python
#-*-coding:utf-8-*-
import StringIO
import json
import random
import string
import time
import hashlib

import pycurl
import urllib


def test_api():
    #TOKEN = 'API'

    tmpurl = 'http://99.1.232.19:81/ansible/web_api/v1_0/auth'
    #tmpurl = 'http://192.168.1.10:80/ansible/web_api/v1_0/auth'
    #sip_list = ['99.1.184.136']
    post_data={'user_name':'test','password':'123456@test'}
    url = tmpurl
    ch = pycurl.Curl()
    ch.setopt(ch.URL, url)
    info = StringIO.StringIO()
    ch.setopt(ch.WRITEFUNCTION, info.write)
    ch.setopt(ch.POST, True)
    ch.setopt(ch.SSL_VERIFYPEER, 0)
    ch.setopt(ch.SSL_VERIFYHOST, 2)
    ch.setopt(ch.HTTPHEADER, ['Content-Type: application/json;charset=utf-8'])
    ch.setopt(ch.POSTFIELDS, json.dumps(post_data))
    #ch.setopt(ch.POSTFIELDS, urllib.urlencode(post_data))
    ch.setopt(ch.HEADER, False)
    ch.perform()
    html = info.getvalue()
    info.close()
    ch.close()
    print html
if __name__ == "__main__":

    test_api()
