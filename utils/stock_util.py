import tushare as ts
import numpy as np
import pandas as pd

import sys
sys.path.append("../utils/")
import token_util
import date_util

pro = token_util.set_token()

def get_stock_list(trade_date=None, delta_price=30.0):
    
    if trade_date is None:
        trade_date = date_util.get_current_date()
    
    stock_list = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name,market,list_date')
    
    stock_list1 = stock_list[~stock_list['market'].isin(["创业板", "科创板"])].reset_index(drop=True)

    delta_date = date_util.get_date_months_before(6)
    stock_list2 = stock_list1[stock_list1["list_date"] <= delta_date].reset_index(drop=True)

    stock_list = stock_list2.drop(['market', 'list_date'], axis=1)
    stock_list['price'] = np.zeros(len(stock_list))
    
    # 剔除 date_time 时刻价格高于30的股票
    
    for i in range(len(stock_list)):
        stock_code = stock_list.iloc[i]["ts_code"]
        try:
            current_df = ts.pro_bar(ts_code=stock_code, adj='qfq',
                                    start_date=trade_date, end_date=trade_date)
            if current_df.empty:
                continue
            stock_list.loc[i, "price"] = (current_df.loc[0, "close"] + current_df.loc[0, "pre_close"]) / 2
        except:
            time.sleep(5)
            
    stock_list = stock_list[stock_list["price"] <= delta_price]
    
    stock_list = stock_list.reset_index(drop=True)
    stock_list.to_csv("../simulate_stock/data/data_{}.csv".format(trade_date), index=False)
    
    return stock_list

def update_stock_daily():
    pass

def get_EMA(data, N):    
    for i in range(len(data)):        
        if i == 0:            
            data.loc[i,'ema'] = data.loc[i,'close']        
        if i > 0:            
            data.loc[i,'ema'] = (2*data.loc[i,'close']+(N-1)*data.loc[i-1,'ema'])/(N+1)
            
    return list(data['ema'])

def cal_macd(ts_code, freq=None, short_=12, long_=26, m=9, ema_short_=7, ema_long_=14, adj='qfq'):
    
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
    
    if freq is None:
        data = ts.pro_bar(ts_code=ts_code, adj=adj)
    else:
        data = ts.pro_bar(ts_code=ts_code, adj=adj, freq=freq)
    
    data = data.sort_values(by="trade_date").reset_index(drop=True)
    
    # 计算 macd
    ema_short = get_EMA(data, short_)
    ema_long = get_EMA(data, long_)
    data['diff'] = pd.Series(ema_short) - pd.Series(ema_long)
    
    for i in range(len(data)):
        if i == 0:
            data.loc[i, 'dea'] = data.loc[i,'diff']        
        else:
            data.loc[i, 'dea'] = (2*data.loc[i,'diff'] + (m-1)*data.loc[i-1,'dea'])/(m+1)  
            
    data["macd"] = 2 * (data['diff'] - data['dea'])
    
    # 计算 ema7 和 ema14
    data["ema7"] = get_EMA(data, ema_short_)
    data["ema14"] = get_EMA(data, ema_long_)
    data = data.drop(['ema'], axis=1)
        
    return data