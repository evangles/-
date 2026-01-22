# -*- coding: utf-8 -*-
"""
每10秒刷新下时时数据反应当前价格
"""
from time import sleep

import tushare as ts

from messge_dingding import messge_ding
import time
def send_meg():
    #设置你的token，登录tushare在个人用户中心里拷贝
    ts.set_token('fe06b251676e15090b6a9c7e835d5f042cadeac46884b71c3d7bb06c')

    #sina数据
    df = ts.realtime_quote(ts_code='600028.SH')
    df=df.loc[:,['NAME','TS_CODE','TIME','PRICE']]
    if df.loc[0,'PRICE']>5.65:

        messge_dingding=df.loc[0].astype(str) #将数据转换成字符
        # print(df)
        meg=" 股票名称{} ，代码{} ，时间{} ,价格{} ".format(messge_dingding[0],messge_dingding[1],messge_dingding[2],messge_dingding[3])

        messge_ding(meg)

if __name__=='__main__':
    while True:
        send_meg()
        time.sleep(10)
    send_meg()


