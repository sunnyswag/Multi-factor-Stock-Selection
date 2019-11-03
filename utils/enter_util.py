import token_util
import date_util
import tushare as ts
import pandas as pd

pro = token_util.set_token()

def get_EMA(data, N):    
    for i in range(len(data)):        
        if i == 0:            
            data.loc[i,'ema'] = data.loc[i,'close']        
        if i > 0:            
            data.loc[i,'ema'] = (2*data.loc[i,'close']+(N-1)*data.loc[i-1,'ema'])/(N+1)
            
    return list(data['ema'])

def cal_macd(ts_code, end_date, short_=12, long_=26, m=9):
    
    '''    
    计算公式：
    3个参数（这3个参数可以根据实际情况自己设定，默认为12，26和9）：
    （12）日快速移动平均线，（26）日慢速移动平均，（9）日移动平均
    
    今日EMA（12）= 前一日EMA（12）×11/13＋今日收盘价×2/13
    今日EMA（26）= 前一日EMA（26）×25/27＋今日收盘价×2/27
    今日DIF = 今日EMA（12）- 今日EMA（26）
    DEA（MACD）= 前一日DEA×8/10＋今日DIF×2/10
    BAR = 2×(DIFF－DEA)
    
    data是包含高开低收成交量的标准dataframe
    short_,long_,m分别是macd的三个参数    
    返回值是包含原始数据和diff,dea,macd三个列的dataframe
    '''
    
    data = ts.pro_bar(ts_code=ts_code, end_date=end_date)
    data = data.sort_values(by="trade_date").reset_index(drop=True)
    
    ema_short = get_EMA(data, short_)
    ema_long = get_EMA(data, long_)
    data['diff'] = pd.Series(ema_short) - pd.Series(ema_long)
    
    for i in range(len(data)):
        if i == 0:
            data.loc[i, 'dea'] = data.loc[i,'diff']        
        else:
            data.loc[i, 'dea'] = (2*data.loc[i,'diff'] + (m-1)*data.loc[i-1,'dea'])/(m+1)  
            
    data['macd'] = 2*(data['diff'] - data['dea'])
    macd = data.loc[len(data)-1, "macd"]
    
    return macd, data['macd']

def cal_ma(ts_code, start_date, end_date, short_=2, long_=5):
    data = ts.pro_bar(ts_code=ts_code, start_date=start_date, end_date=end_date, ma=[short_, long_])
    ma2_1, ma2_2 = data.loc[1, "ma{}".format(short_)], data.loc[0, "ma{}".format(short_)]
    ma5_1, ma5_2 = data.loc[1, "ma{}".format(long_)], data.loc[0, "ma{}".format(long_)]
    
    return ma2_1, ma2_2, ma5_1, ma5_2