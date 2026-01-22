# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 14:35:55 2024

@author: Administrator
1 生成boll 模型数据集，集合股息，及当前数据
2 生成相关分析表格，收益情况
3 生成盯盘指标等发送实时数据
4 根据图形情况生成图像数据
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
class S_kdj(object):
    # 以证券的品种及长线短线作为参数
    '''n为整个周期，k_n,k线的平滑周期，d_n,线的平滑周期'''
    def __init__(self,ts_code,N,K_n,D_n):

        y_day = datetime.date.today() +datetime.timedelta(days=-1)#获取前一个交易日日期作为历史数据节点
        self.ts_code=ts_code
        self.N = N
        self.K_n=K_n
        self.D_n=D_n
        self.start_date ='20250501'
        self.stop_date =y_day.strftime("%Y%m%d")#统一时间数据格式



    def kdj_stock_divident(self):#增加股息补偿,添加最新价格
        df_div = divident(self.ts_code[:6])#股息表格
        df1 = stock_histroy_daliy(self.ts_code, self.start_date, self.stop_date)#应用基于tushare
        df1['date']=df1['date'].apply(lambda x: x.date())#用匿名函数修改数据类型修改为date 数据



        df2=ontime_compend(self.ts_code)#引入实时数据，下一步合并
        df1=pd.concat([df1,df2],axis=0)
        # df1.to_excel('.//历史+及时股价.xlsx', index=False)

        #====================================================

        df=pd.merge(df1,df_div,left_on='date',right_on='date',how='left')#将股息表合并


        # 汇总历史及股息数据
        # kdj策略指标绘制

        #计算指标
        df['low_n'] = df['close'].rolling(self.N).min()
        df['high_n'] = df['close'].rolling(self.N).max()

        df['RSV'] = round((df['close']-df['low_n'])/(df['high_n']-df['low_n'])*100,1)
        df['RSV']=df['RSV'].replace([np.inf, -np.inf], np.nan).fillna(50)
        # 设置初始K，D值
        df['k']=50
        df['d']=50
        for i in range(1,len(df)):
            df.loc[i, 'k'] = (2 / 3) * df.loc[i - 1, 'k'] + (1 / 3) * df.loc[i, 'RSV']
            df.loc[i, 'd'] = (2 / 3) * df.loc[i - 1, 'd'] + (1 / 3) * df.loc[i, 'k']
        df['j']=3*df['k']-2*df['d']

        #生成KDJ原始图表数据
        # df_pic=df.loc[:,['date','k','d','j']]
        # df_pic.to_excel('.//kdj_pic.xlsx', index=False)


        #图表实验展示
        # df=df.loc[:,['date','k','d','j']]
        # fig = plt.figure()
        # ax1 = fig.add_subplot(111)
        # ax1.plot(df['k'], color='b', label='k')
        # ax1.plot(df['d'], color='r', label='d')
        # ax1.plot(df['j'], color='g', label='j')
        # plt.show()


        # # ==============================
        # # 生成信号，！当前价格 前后一天有变化
        df['signal_long'] = (df['k'].shift(1) <= df['d'].shift(1)) & (df['k'] > df['d'])&(df['k']<20) # shift 1 数据向下位移做多信号

        df['signal_short'] = (df['k'].shift(1) >= df['d'].shift(1)) & (df['k'] < df['d'])&(df['k']>80)  # 做空新号


        df = df[(df['signal_long'] == True) | (df['signal_short'] == True)|(df['divident'].notnull())]#获取股息，及相关新号指标
        df['signal_div']=df['divident'].notnull()
        df.to_csv('.//'+str(self.ts_code)+'_signal_kdj.csv',index=False,encoding='utf-8-sig')

        return df # 返回表格







    def re_divdent(self):#回溯模块
        df=self.kdj_stock_divident()
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
        dic_return['profit_cum_list']=profit_cum_list
        return dic_return #注意加返回语句

    #此处=================================================


    def stock_divident_meg(self):  # 增加股息补偿发送通知
        df=self.kdj_stock_divident()

        df2 = ontime_compend(self.ts_code)  # 引入实时数据，下一步合并
        # 生成相应的买入卖出信号
        if df.tail(1).iloc[0, 0] == df2.iloc[0, 0]:#日期相等时候

            if df.tail(1).iloc[0, 11] == True:
                messge_ding('买入信号' + str(self.ts_code) + 'kdj-' +  str(self.N)+ '，'+str(self.K_n)+ '，'+str(
                    self.D_n) + '当前价格' + str(df.tail(1).iloc[0, 1]))
            elif df.tail(1).iloc[0, 12] == True:
                messge_ding('卖出信号' + str(self.ts_code) + 'kdj-' + str(self.N) + '，' + str(self.K_n) + '，' + str(
                        self.D_n) + '当前价格' + str(df.tail(1).iloc[0, 1]))

        return self.ts_code,df.tail(1)['date'],df.tail(1)['close']
    def pic (self):
        self.boll_stock_divident()
        return_re=self.re_divdent()
        df_pic=pd.read_excel('.//pic.xlsx')
        fig=plt.figure()
        ax1=fig.add_subplot(211)
        ax2 = fig.add_subplot(212)
        df_pic = df_pic.set_index('date')
        ax1.plot(df_pic['close'],color='b',label='close')
        ax1.plot(df_pic['up'],color='r',label='up')
        ax1.plot(df_pic['down'],color='g',label='down')

        #效果不好不展示标注点了
        # df_pic_singal_long=df_pic['signal_long'].values#方便便利
        # for j in range(len(df_pic['close'])):
        #     if  df_pic_singal_long[j]==True:
        #        ax1.annotate('buy', xy=(j, df_pic_singal_long[j]),xytext=(j, df_pic_singal_long[j]+20),arrowprops={'arrowstyle':'->'})

        ax1.legend()
        ax2.plot(return_re['profit_cum_list'])
        print(return_re)
        # plt.annotate('long',xy=(df_pic['signal_long']))

        plt.show()

    


if __name__=='__main__':
    ts_code = '600028.SH'
    N=9
    K_n=3
    D_n=3
    a=S_kdj(ts_code,N,K_n,D_n)

    # df=a.kdj_stock_divident()
    # print(df)
    df=a.re_divdent()
    # df=a.stock_divident_meg()
    #
    print(df)#打印返回值
    # a.pic()
       
