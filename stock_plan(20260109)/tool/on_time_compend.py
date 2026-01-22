from itertools import groupby

import tushare as ts
import time
import pandas as pd
import datetime
'''用于合成及时数据，将实时数据每几秒刷新合成，传给策略函数'''


def ontime_compend(af_code):
    turn_dic={}#设置空字典，填入相关信息要素
    i = 0
    df_all =ts.realtime_quote(af_code)
    while i < 5:
        a=ts.realtime_quote(af_code)
        # df_all=df_all.append(a)
        df_all = pd.concat([df_all, a], axis=0)
        i += 1
        time.sleep(1)
    # print(df_all)
    # 获取最新报价
    df_all = df_all.loc[:, ['DATE', 'PRICE']]
    df_all.columns = ['date', 'close']
    # df_all.iloc[0, 0]=datetime.datetime.strptime(df_all.iloc[0, 0],'%Y-%m-%d')#格式不匹配
    # print(type(df_all.iloc[0, 0]))
    # df_all.to_excel('.//212.xlsx', index=True)
    # turn_dic['date']=pd.Timestamp(df_all.iloc[0,0])
    turn_dic['date']=datetime.date.today()
    turn_dic['close'] =round(df_all['close'].mean(),2)
    df=pd.DataFrame(turn_dic,index=[0])
    return df

if __name__=='__main__':
   df=ontime_compend('600000.SH')
   print(df)
   df=pd.DataFrame(df,index=[0])

   df.to_excel('.//21.xlsx',index=False)

   print(type(df))