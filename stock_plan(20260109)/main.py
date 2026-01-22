''''调用集成所有函数'''
import pandas as pd
from strategy.stock_sma import S_sma #注意类文件不是函数，可以直接导入类
from strategy.stock_boll import S_boll
from strategy.stock_kdj import S_kdj
from datetime import datetime
import time
from tool.messge_dingding import messge_ding
class main(object):
    def __init__(self,patch_bath,patch_msg):
        self.patch_bath=patch_bath
        self.patch_msg=patch_msg
        # self.time_start01=[13, 27]
        # self.time_start02= [13, 30]
        # self.time_stop01 = [11, 30]
        # self.time_stop02 = [15, 0]



    def sma_selet_stock_batch(self):#批量筛选股票数据选择收益最平稳最高的
        df_sel=pd.read_excel(self.patch_bath)
        for i in range(0,len(df_sel)):
            a = S_sma(df_sel.iloc[i,0], df_sel.iloc[i,1], df_sel.iloc[i,2])
    #批量输出指标
    #==========================================================================
            dic_return = a.re_divdent()
            df_sel.loc[i,'profit_cum_nao']=dic_return['profit_cum_nao']
            df_sel.loc[i,'times']= dic_return['times']
            df_sel.loc[i,'profit_mean']=dic_return['profit_mean']
            df_sel.loc[i, 'profit_cum_nao_ratio/year'] = dic_return['profit_cum_nao_ratio/year']
            df_sel.loc[i, 'max_loss_ratio'] = dic_return['max_loss_ratio']
            df_sel.loc[i, 'win_ratio'] = dic_return['win_ratio']
            df_sel.loc[i, 'mean_squared_deviation'] = dic_return['mean_squared_deviation']
            df_sel.loc[i,'divident']=dic_return['divident']
        df_sel.to_excel('.//out_table//out_result.xlsx',index=False)
    def sma_selet_stock_ontime(self):#根据上述筛选结果逐盘盯盘(多个股票随时盯盘)
        df_sel = pd.read_excel(self.patch_msg)
        for i in range(0, len(df_sel)):
            a = S_sma(df_sel.iloc[i, 0], df_sel.iloc[i, 1], df_sel.iloc[i, 2])
            df = a.stock_divident_meg()
            print(df)
    def sma_run_msg_plantime(self):
        # 定时任务定时开机，并在收盘前关闭


        while True:
            now = datetime.now()
            if now.hour == self.time_start01[0] and now.minute == self.time_start01[1]:
                while True:
                    print('ok')
                    self.selet_stock_ontime()
                    time.sleep(600)
            elif now.hour == self.time_stop02[0] and now.minute == self.time_stop02[1]:
                break
            time.sleep(60)
#================================boll++++++++++++++++++++=
    def boll_selet_stock_batch(self):#批量筛选股票数据选择收益最平稳最高的
        df_sel=pd.read_excel(self.patch_bath)
        for i in range(0,len(df_sel)):
            a = S_boll(df_sel.iloc[i,0], df_sel.iloc[i,1], df_sel.iloc[i,2],df_sel.iloc[i,3])
    #批量输出指标
    #==========================================================================
            dic_return = a.re_divdent()
            df_sel.loc[i,'profit_cum_nao']=dic_return['profit_cum_nao']
            df_sel.loc[i,'times']= dic_return['times']
            df_sel.loc[i,'profit_mean']=dic_return['profit_mean']
            df_sel.loc[i, 'profit_cum_nao_ratio/year'] = dic_return['profit_cum_nao_ratio/year']
            df_sel.loc[i, 'max_loss_ratio'] = dic_return['max_loss_ratio']
            df_sel.loc[i, 'win_ratio'] = dic_return['win_ratio']
            df_sel.loc[i, 'mean_squared_deviation'] = dic_return['mean_squared_deviation']
            df_sel.loc[i,'divident']=dic_return['divident']
        df_sel.to_excel('.//out_table//out_result.xlsx',index=False)
    def boll_selet_stock_ontime(self):#根据上述筛选结果逐盘盯盘(多个股票随时盯盘)！！ 还没有调试
        df_sel = pd.read_excel(self.patch_msg)
        for i in range(0, len(df_sel)):
            a = S_boll(df_sel.iloc[i, 0], df_sel.iloc[i, 1], df_sel.iloc[i, 2],df_sel.iloc[i, 3])
            df = a.stock_divident_meg()
            print(df)
#============================kdj===================================================
    def kdj_selet_stock_batch(self):#批量筛选股票数据选择收益最平稳最高的
        df_sel=pd.read_excel(self.patch_bath)
        for i in range(0,len(df_sel)):
            a = S_kdj(df_sel.iloc[i,0], df_sel.iloc[i,1], df_sel.iloc[i,2],df_sel.iloc[i,3])
    #批量输出指标
    #==========================================================================
            dic_return = a.re_divdent()
            df_sel.loc[i,'profit_cum_nao']=dic_return['profit_cum_nao']
            df_sel.loc[i,'times']= dic_return['times']
            df_sel.loc[i,'profit_mean']=dic_return['profit_mean']
            df_sel.loc[i, 'profit_cum_nao_ratio/year'] = dic_return['profit_cum_nao_ratio/year']
            df_sel.loc[i, 'max_loss_ratio'] = dic_return['max_loss_ratio']
            df_sel.loc[i, 'win_ratio'] = dic_return['win_ratio']
            df_sel.loc[i, 'mean_squared_deviation'] = dic_return['mean_squared_deviation']
            df_sel.loc[i,'divident']=dic_return['divident']
        df_sel.to_excel('.//out_table//out_result.xlsx',index=False)

    def kdj_selet_stock_ontime(self):#根据上述筛选结果逐盘盯盘(多个股票随时盯盘)！！ 还没有调试
        df_sel = pd.read_excel(self.patch_msg)
        for i in range(0, len(df_sel)):
            a = S_kdj(df_sel.iloc[i, 0], df_sel.iloc[i, 1], df_sel.iloc[i, 2],df_sel.iloc[i, 3])
            df = a.stock_divident_meg()
            print(df)

if __name__=='__main__':

    # messge_ding('程序启动')
    sma_patch_bath = './/input_table//sma_strategy_bath.xlsx'
    sma_patch_msg='.//input_table//sma_strategy_msg.xlsx'

    boll_patch_bath = './/input_table//boll_strategy_bath.xlsx'
    boll_patch_msg='.//input_table//boll_strategy_msg.xlsx'

    kdj_patch_bath='.//input_table//kdj_strategy_bath.xlsx'
    kdj_patch_msg='.//input_table//kdj_strategy_msg.xlsx'

    #==========================================
    # a = main(sma_patch_bath, sma_patch_msg)
    #
    # a.sma_selet_stock_batch()#运行各种组合表现
    # ========================================
    # a.sma_selet_stock_ontime()#只有当然情况才发同志，目前返回最后一条符合策略的价格

    # a.sma_run_msg_plantime()#按设定时间运行筛选符合策略方案# 基本通过主机crontab 设置所代替
#————————————————————————————————————————————————————————————————————————————————————
    # b = main(boll_patch_bath, boll_patch_msg)
    # b.boll_selet_stock_batch()
    # b.boll_selet_stock_ontime()
    # ========================================
    #kdj 指标计算
    c = main(kdj_patch_bath, kdj_patch_msg)
    c.kdj_selet_stock_batch()
    # c.kdj_selet_stock_ontime()