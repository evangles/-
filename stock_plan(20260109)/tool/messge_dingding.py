# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 08:26:01 2025

@author: Administrator
"""

import requests
import json
def messge_ding(meg):
    # messge_ding='xiaoxi'
    # 钉钉机器人的Webhook URL
    webhook = 'https://oapi.dingtalk.com/robot/send?access_token=dfbc5f50602b6ba13e754587c7a7b5e3799fcebb3ad68c8eb9d46254d4711311'
    headers = {'Content-Type': 'application/json'}

    # 消息内容
    text = {
    'msgtype': 'text',
    'text': {
    'content': '通知:'+meg
    }
    }

    # 发送POST请求
    response = requests.post(url=webhook, headers=headers, data=json.dumps(text))

    # 打印响应结果
    # print(response.status_code)
    # print(response.text)
