'''根据tushare平台，通过试试和时时两个函数调取传入数据'''
import tushare as ts
taken='fe06b251676e15090b6a9c7e835d5f042cadeac46884b71c3d7bb06c'
ts.set_token(taken)
class Get_data(object):
    def __init__(self,ts_code):
        self.ts_code=ts_code
    def data_ontime(self):#生成实时的数据
        df = ts.realtime_quote(self.ts_code)
        print(df)
        return df
    def data_history(self,start_date='20180701',end_date='20250329'):#历史数据从截至时间段
        pro = ts.pro_api()
        df = pro.daily(ts_code=self.ts_code)
        print(df)
if __name__=='__main__':

   Get_data('600028.SH').data_ontime()
   Get_data('600028.SH').data_history()
   
   
  
