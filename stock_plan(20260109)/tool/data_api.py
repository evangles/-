import akshare as ak
import pandas as pd
import tushare as ts
"""股票应用tushare 库-ts_code，期货akshare 库参数-af_code

"""

def getdel_data(af_code):#应用于concat 多列生成hotmap,基于akshare,将列标题处理并以参数命名
    futures_zh_daily_sina_df = ak.futures_zh_daily_sina(symbol=af_code)
    df = futures_zh_daily_sina_df
    df = df.loc[:, ['date', 'close']]
    df = df.set_index('date')#将时间序列转为index，方便合并
    df.columns = [af_code]
    return df
def futures_zh_daily_sina(af_code):#ak.futures_hist_table_em()调取期货品种，按照天
    # columns=[date    open    high     low   close  volume  hold  settle]
    df = ak.futures_zh_daily_sina(symbol=af_code)
    df=df.loc[:,['date','close']]

    return df
def futures_zh_minute_sina(af_code,zq):#生成分钟图period参数范围(1.5.15，30，60)
    #columns='datetime', 'open', 'high', 'low', 'close', 'volume', 'hold'
    df = ak.futures_zh_minute_sina(symbol=af_code, period=zq)
    df=df.loc[:,['datetime','close']]
    df.columns=['date','close']
    return df
#===========================================================================================
#以上是期货部分，以下是股票部分
def stock_ontime(ts_code):
    ''''collumns=['NAME', 'TS_CODE', 'DATE', 'TIME', 'OPEN', 'PRE_CLOSE', 'PRICE', 'HIGH',
       'LOW', 'BID', 'ASK', 'VOLUME', 'AMOUNT', 'B1_V', 'B1_P', 'B2_V', 'B2_P',
       'B3_V', 'B3_P', 'B4_V', 'B4_P', 'B5_V', 'B5_P', 'A1_V', 'A1_P', 'A2_V',
       'A2_P', 'A3_V', 'A3_P', 'A4_V', 'A4_P', 'A5_V', 'A5_P']
    '''
    #设置你的token，登录tushare在个人用户中心里拷贝
    ts.set_token('fe06b251676e15090b6a9c7e835d5f042cadeac46884b71c3d7bb06c')

    #sina数据
    df = ts.realtime_quote(ts_code=ts_code)
    # df=df.loc[:,['NAME','TS_CODE','TIME','PRICE']]
    df = df.loc[:, ['TIME','PRICE']]
    df.columns = ['date', 'close']
    return df
def stock_histroy_daliy(ts_code,start_date,end_date):
    #'ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'pre_close', 'change', 'pct_chg', 'vol', 'amount']
    #设置你的token，登录tushare在个人用户中心里拷贝
    ts.set_token('fe06b251676e15090b6a9c7e835d5f042cadeac46884b71c3d7bb06c')
    pro = ts.pro_api()

    df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
    df=df[::-1]#将顺序调整
    df = df.loc[:, ['trade_date','close']]
    df.columns = ['date', 'close']


    df['date']=pd.to_datetime(df['date'])
    # df.to_excel('.//60028.xlsx')
    print(type(df.iloc[0,0]))
    return df
def divident(ts_code):#目前不太用于调用
    ''''stock_fhps_detail_em_df = ak.stock_fhps_detail_em(symbol="300073")
print(stock_fhps_detail_em_df)'''
    '''''报告期', '业绩披露日期', '送转股份-送转总比例', '送转股份-送股比例', '送转股份-转股比例', '现金分红-现金分红比例',
       '现金分红-现金分红比例描述', '现金分红-股息率', '每股收益', '每股净资产', '每股公积金', '每股未分配利润',
       '净利润同比增长', '总股本', '预案公告日', '股权登记日', '除权除息日', '方案进度', '最新公告日期'],'''
    df = ak.stock_fhps_detail_em(symbol=ts_code)
    df = df.loc[:, ['除权除息日', '现金分红-现金分红比例','送转股份-转股比例','现金分红-现金分红比例描述']]
    df.columns = ['date', 'divident','ratio','detail']
    # print(type(df.iloc[0,0]))
    return df
if __name__=='__main__':#600000.SH rb2602
    ts_code='600000.SH'
    af_code='rb2602'
    zq=60
    # df=stock_histroy_daliy('600000.SH', start_date='20240105', end_date='20250519')
    df=divident(ts_code)
    print(df)