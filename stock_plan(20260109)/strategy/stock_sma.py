# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 14:35:55 2024

@author: Administrator
"""
import sys
import datetime
import matplotlib.pyplot as plt

sys.path.insert(0, "..")#添加路径导入上级的函数
from tool.data_api import futures_zh_daily_sina,futures_zh_minute_sina,stock_ontime,stock_histroy_daliy,divident
# import akshare as ak
from tool.on_time_compend import ontime_compend
import pandas as pd
import numpy as np
from tool.messge_dingding import messge_ding
class S_sma(object):
    # 以证券的品种及长线短线作为参数
    def __init__(self,ts_code,short_size,long_size):
        y_day = datetime.date.today() - datetime.timedelta(days=-1)
        self.ts_code=ts_code
        self.short_size = short_size
        self.long_size=long_size
        self.start_date ='20230501'
        self.stop_date =y_day.strftime("%Y%m%d")
    def sma(self): #暂且不用
        # 删选列表
        # df=futures_zh_daily_sina(self.ts_code)
        df=stock_histroy_daliy(self.ts_code,self.start_date,self.stop_date)

        df.index=df.pop('date')#删除并将日期作为索引



        # 向下偏移一个单位的目的是避免未来函数，以为不向下偏移会计算当前价格
        df['mean_short']=df['close'].rolling(self.short_size).mean()
        df['short']=df['mean_short'].shift(1)
        
        df['mean_long']=df['close'].rolling(self.long_size).mean()
        df['long']=df['mean_long'].shift(1)



        # 生成列表
        df['signal_long']=(df['short'].shift(1)<=df['long'].shift(1))&(df['short']>df['long'])#做多信号

        df['signal_short']=(df['short'].shift(1)>=df['long'].shift(1))&(df['short']<df['long'])#做空新号
        df=df[(df['signal_long']==True)|(df['signal_short']==True)]
        # df.to_excel('.//zhibiaoxian.xlsx')

        return df   # 返回表格##
    def sma_stock_divident(self):#增加股息补偿
        df_div = divident(self.ts_code[:6])
        df1 = stock_histroy_daliy(self.ts_code, self.start_date, self.stop_date)#应用基于tushare
        df1['date']=df1['date'].apply(lambda x: x.date())#用匿名函数修改数据类型


        # df1.index = df1.pop('date')  # 删除并将日期作为索引
        df2=ontime_compend(self.ts_code)#引入实时数据，下一步合并
        df1=pd.concat([df1,df2],axis=0)
        # df1.to_excel('.//历史+最新数据.xlsx', index=False)
        #====================================================

        df=pd.merge(df1,df_div,left_on='date',right_on='date',how='left')


        # 向下偏移一个单位的目的是避免未来函数，以为不向下偏移会计算当前价格
        df['mean_short'] = df['close'].rolling(self.short_size).mean()
        df['short'] = df['mean_short'].shift(1)

        df['mean_long'] = df['close'].rolling(self.long_size).mean()
        df['long'] = df['mean_long'].shift(1)
        # ==============================
        # 生成列表
        df['signal_long'] = (df['short'].shift(1) <= df['long'].shift(1)) & (df['short'] > df['long'])  # 做多信号

        df['signal_short'] = (df['short'].shift(1) >= df['long'].shift(1)) & (df['short'] < df['long'])  # 做空新号
        df.to_excel('.//pic.xlsx', index=False)
        df = df[(df['signal_long'] == True) | (df['signal_short'] == True)|(df['divident'].notnull())]#获取股息，及相关新号指标
        df['signal_div']=df['divident'].notnull()
        df.to_excel('.//signal_sma.xlsx',index=False)

        return df # 返回表格





    def re_sma(self):#回溯模块
        df=self.sma()
        profit_cum_list = []  # 初始收益列表
        profit_cum = 0
        #================================
        cash = 50000#初始金额
        hold_cash=0#初始金额0
        commission_ratio = 0.0002#佣金率
        slippage_ratio = 0.0001#滑点率
        Positions_ratio=0.7#仓位操作率
        bill_s=0#持有股票数量
        trans_fee=5#交易费5元


        #================================
        hold_state = 0  # 持仓状态
        hold_price_A = 0  # 持仓价格
        dic_return = {} #需要返回的指标数据等
        divident_cash_sum = 0  # 股息初始为0

        sig_long = df['signal_long']
        sig_short = df['signal_short']
        price = df['close'].values

        # 1/2仓买入全仓出

        for i in range(0, len(price)):
            if hold_state == 0:  # 当未持仓时候，判断产生持多的信号后，产生当前价格，打开持仓状态
                if sig_long[i] == True:
                    hold_price_A = price[i]
                    hold_state = 1
                    bill_s=round((0.01*Positions_ratio*cash)/hold_price_A)#持有证券数量
                    cash=cash-(bill_s*hold_price_A)*100*(1+slippage_ratio+slippage_ratio)#现金余额

                    hold_cash=hold_price_A*bill_s*100#证券资产
                    catpital=cash + hold_cash
                    # print(cash,hold_price_A, bill_s, hold_cash,catpital,'买入')
            else:  # 当持仓状态并且产向下的信号时候,卖出，并累计收益
                if hold_state == 1 and sig_short[i] == True:
                    profit = (price[i]-hold_price_A)*100*bill_s
                    profit_cum += profit
                    hold_state = 0
                    cash=cash+price[i]*100*bill_s-trans_fee
                    # print(cash,price[i],'卖出')
                    hold_cash=0#持有股票清零
                    bill_s=0#持有股票数量清零
                    catpital = cash + hold_cash+divident_cash_sum

        profit_cum_list.append(profit_cum)
        # print(profit_cum_list,profit_cum)
        # 返回一个字典返回相关的标准值，以字典的形式
        dic_return['profit_cum_nao'] = round(profit_cum,3)
        dic_return['times'] = len(profit_cum_list)
        dic_return['cash']=round(cash)
        dic_return['catpital']=catpital
        dic_return['divdent'] = divident_cash_sum
        return dic_return

    def re_divdent(self):#回溯模块
        df=self.sma_stock_divident()
        # print(df)
        profit_cum_list = []  # 初始收益列表
        profit_list=[] #计算每笔的盈亏情况
        profit_cum = 0
        #================================
        cash = 50000#初始金额
        hold_cash=0#初始金额0
        commission_ratio = 0.0002#佣金率
        slippage_ratio = 0.0001#滑点率
        Positions_ratio=1#仓位操作率
        bill_s=0#持有股票数量
        trans_fee=5#交易费5元
        divident_cash_sum=0#股息初始为0


        #================================
        hold_state = 0  # 持仓状态
        hold_price_A = 0  # 持仓价格
        dic_return = {} #需要返回的指标数据等
        # ======================================================
        sig_long = df['signal_long'].values #!!!!注意此添加values
        sig_short = df['signal_short'].values
        price = df['close'].values
        divident=df['divident'].values
        sig_div=df['signal_div'].values
        date=df['date'].values
        # ======================================================
        # 1/2仓买入全仓出
        for i in range(0, len(price)):
            # if hold_state == 0 and sig_long[i] == True:  # 当未持仓时候，判断产生持多的信号后，产生当前价格，打开持仓状态
            if hold_state == 0 and sig_long[i] == True:  # 当未持仓时候，判断产生持多的信号后，产生当前价格，打开持仓状态
                hold_price_A = price[i]#记录买入价格
                hold_state = 1

                bill_s=round((0.01*Positions_ratio*cash)/hold_price_A)#持有证券数量
                cash=cash-(bill_s*hold_price_A)*100*(1+slippage_ratio+slippage_ratio)#现金余额

                hold_cash=hold_price_A*bill_s*100#证券资产
                # print(date[i],'买入','单价',hold_price_A, '数量/手',bill_s,'可用资金',round(cash,2),'持有资产',round(hold_cash,2))
                catpital=cash + hold_cash+divident_cash_sum+divident_cash_sum

             # 先贴息，再处置卖出
            else:
                if hold_state == 1 and sig_div[i] ==True:
                    divident_cash = divident[i] * bill_s * 10
                    divident_cash_sum += divident_cash

                elif hold_state == 1 and sig_short[i] == True:
                    profit = (price[i] - hold_price_A) * 100 * bill_s
                    profit_cum += profit
                    profit_list.append(profit)
                    hold_state = 0#调整空仓
                    cash = cash + price[i] * 100 * bill_s - trans_fee
                    hold_cash = 0  # 持有股票清零
                    bill_s = 0  # 持有股票数量清零
                    catpital = cash + hold_cash + divident_cash_sum
                    profit_cum_list.append(profit_cum)
                    # print(date[i],'卖出', '单价', price[i], '数量/手', bill_s, '可用资金', round(cash), '持有资产',round(hold_cash, 2))

        #======================================================
        '''以下为需要输出的指标'''
        # print(profit_cum_list)#打印利润表
        # print(profit_list)#打印配对交易
        d_s=pd.Series(profit_list) #转成Series 方便计算方差


        dic_return['profit_cum_nao'] = round(profit_cum,3)
        dic_return['times'] = len(profit_cum_list)
        # dic_return['cash']=round(cash)
        # dic_return['catpital']=round(catpital,2)
        dic_return['divident'] = round(divident_cash_sum, 2)
        dic_return['profit_mean']=round(np.mean(profit_list),2)
        dic_return['profit_cum_nao_ratio/year']=round((profit_cum/catpital)/2,2)
        dic_return['max_loss_ratio'] = round(np.min(profit_list)/catpital, 2)#初始金额
        dic_return['win_ratio']=round(len([num for num in profit_list if num >0 ])/len(profit_list),2)
        dic_return['mean_squared_deviation']=round(d_s.std(ddof=0),2)#返回平均方差
        dic_return['profit_cum_list'] = profit_cum_list
        return dic_return #注意加返回语句


    def stock_divident_meg(self):  # 增加股息补偿发送通知

        # 返回实时数据
        df2 = ontime_compend(self.ts_code)
        df=self.sma_stock_divident()
        # 生成相应的买入卖出信号
        if df.tail(1).iloc[0, 0] == df2.iloc[0, 0]:

            if df.tail(1).iloc[0, 9] == True:
                messge_ding('买入信号' + str(self.ts_code) + ' ' + str(self.short_size) + '短均线-长均线' + str(
                    self.long_size) + '当前价格' + str(df.tail(1).iloc[0, 1]))
            elif df.tail(1).iloc[0, 10] == True:
                messge_ding('卖出信号' + str(self.ts_code) + ' ' + str(self.short_size) + '短均线-长均线' + str(
                    self.long_size) + '当前价格' + str(df.tail(1).iloc[0, 1]))

        return self.ts_code,df.tail(1)['date'],df.tail(1)['close']

    def pic (self):
        self.sma_stock_divident()
        return_re = self.re_divdent()
        df_pic=pd.read_excel('.//pic.xlsx')
        fig=plt.figure()
        ax1=fig.add_subplot(211)
        ax2 = fig.add_subplot(212)
        df_pic = df_pic.set_index('date')
        # ax1.plot(df_pic['close'])

        ax1.plot(df_pic['long'],label='long')
        ax1.plot(df_pic['short'],label='short')
        ax1.plot(df_pic['close'], label='pice')
        ax2.plot(return_re['profit_cum_list'])
        print(return_re)
        ax1.legend()
        plt.show()



if __name__=='__main__':
    af_code = '600030.SH'
    # af_code = 'rb2506'
    short_size = 5
    long_size=15

    #截至获取前一天数据==================

    # ===============================

    a=S_sma(af_code,short_size,long_size)#先实例化

    # df=a.re_divdent()#含有贴息，报错

    # df=a.sma_stock_divident_meg()
    # df=a.sma_stock_divident()

    # print(df)#打印返回值
    a.pic()

       
