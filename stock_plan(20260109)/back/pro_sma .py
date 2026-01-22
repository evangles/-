# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 14:35:55 2024

@author: Administrator
"""
import sys
sys.path.insert(0, "..")#添加路径导入上级的函数
from funtion_all import getK_data,data_get_min
import akshare as ak
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
class F_sma(object):
    # 以证券的品种及长线短线作为参数
    def __init__(self,pinming,long_size,short_size):
        self.pinming=pinming
        self.long_size=long_size
        self.short_size=short_size

    def sma(self):
        # 删选列表
        df=getK_data(self.pinming)
        df.index=df.pop('date')

        df=df.loc[:,['close','volume']]
       
        df['p_short']=df['close'].rolling(self.short_size).mean()
        df['short']=df['p_short'].shift(1)
        
        df['p_long']=df['close'].rolling(self.long_size).mean()
        df['long']=df['p_long'].shift(1)
        

        # 图表
        # plt.subplot(211)
        # plt.plot(df['close'])
        # plt.plot(df['short'])
        # plt.plot(df['long'])
        # plt.xticks([])
        # plt.legend()
        # plt.subplot(212)
        # plt.plot(df['volume'])
        # plt.xticks(df.index[::30],rotation = 45)
        # 生成列表
        df['signal_long']=(df['short'].shift(1)<=df['long'].shift(1))&(df['short']>df['long'])
        df['signal_short']=(df['short'].shift(1)>=df['long'].shift(1))&(df['short']<df['long'])
        df=df[(df['signal_long']==True)|(df['signal_short']==True)]
        # 开始遍历 分析价格
        profit_cum_list = []  # 初始收益列表
        profit_cum = 0
        
        hold_state = 0  # 持仓状态
        hold_price_A = 0  # 持仓价格
        dic_return={}
 
        sig_long=df['signal_long']
        sig_short=df['signal_short']
        price=df['close'].values

        for i in range(0,len(price)):
            if hold_state==0:#当未持仓时候，判断产生持多的信号后，产生当前价格，打开持仓状态
                if sig_long[i]==True:
                    hold_price_A=price[i]
                    hold_state=1
            else:#当持仓状态并且产向下的信号时候,卖出，并累计收益
                if hold_state==1 and sig_short[i]==True:
                    profit=hold_price_A-price[i]
                    profit_cum+=profit
                    hold_state=0 
            profit_cum_list.append(profit_cum)
        # print(profit_cum_list,profit_cum)
        # 返回一个字典返回相关的标准值，以字典的形式
        dic_return['profit_cum']=profit_cum
        dic_return['times']=len(profit_cum_list)
        return dic_return

if __name__=='__main__':
    # dic_F={'F_list':['rb2412','rb2411','i2412','j2412'],'window_size':[15,3]}
    # a=F_sma(dic_F['F_list'][0])
    # a.sma()
    # a=F_sma('rb2412',5,3).sma()
    # print(a)
    # a.sma()
    df_t=pd.read_excel('.//ceyue.xlsx')
    for i in range(0,len(df_t['pinming'])):
        df_t['profit_sum'][i]=(F_sma(df_t['pinming'][i],df_t['long'][i],df_t['short'][i]).sma())['profit_cum']#f返回交易利润
        df_t['times'][i]=(F_sma(df_t['pinming'][i],df_t['long'][i],df_t['short'][i]).sma())['times']#返回交易次数
    # df_t.to_excel('.//1234.xlsx')
    print(df_t)
       
       
