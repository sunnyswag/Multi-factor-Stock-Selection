import tushare as ts
import numpy as np
import pandas as pd
import os

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

def get_EMA(data, N, update):
    
    start = 1 if update else 0
    
    for i in range(start, len(data)):        
        if i == 0:            
            data.loc[i,'ema{}'.format(N)] = data.loc[i,'close']        
        else:
            data.loc[i,'ema{}'.format(N)] = (2*data.loc[i,'close']+(N-1)*data.loc[i-1,'ema{}'.format(N)])/(N+1)
            
    return list(data['ema{}'.format(N)])

def cal_macd(data, update, short_=12, long_=26, m=9):
    
    ema_short = get_EMA(data, short_, update)
    ema_long = get_EMA(data, long_, update)
    data['diff'] = pd.Series(ema_short) - pd.Series(ema_long)
    
    start = 1 if update else 0
    
    for i in range(start, len(data)):
        if i == 0:
            data.loc[i, 'dea'] = data.loc[i,'diff']        
        else:
            data.loc[i, 'dea'] = (2*data.loc[i,'diff'] + (m-1)*data.loc[i-1,'dea'])/(m+1)  
            
    data["macd"] = 2 * (data['diff'] - data['dea'])
    
    return data

def pull_data(ts_code, root_dir, freq=None, adj='qfq'):
    
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
        root_dir = os.path.join(root_dir, "day")
    elif freq == 'W':
        root_dir = os.path.join(root_dir, "week")
    else:
        root_dir = os.path.join(root_dir, "month")
    
    root_dir = os.path.join(root_dir, "{}.csv".format(ts_code))
    
    # 更新数据
    if os.path.exists(root_dir):
        data = pd.read_csv(root_dir)
        
        # 获取开始和结束时间
        start_date = str(data.iloc[-1]["trade_date"]+1)
        end_date = date_util.get_current_date()

        if int(start_date) > int(end_date):
            return
        else:
            update = True
            
            data_tmp = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
            
            # 在 data_tmp中构造data中所有的列，以便和data合并
            for column in data.columns:
                if column not in data_tmp.columns:
                    data_tmp[column] = data_tmp["change"]
            
            # 将data的最后一行数据插入到data_tmp中，以便计算macd,dif,eda
            data_last = pd.DataFrame(np.array(data.iloc[-1]).reshape(1,-1), columns=data_tmp.columns)
            data_tmp = pd.concat([data_last, data_tmp], ignore_index=True)
            
            # 计算结果并和data合并
            data_tmp = cal_macd(data_tmp, update)
            data = pd.concat([data, data_tmp.drop(0)], ignore_index=True)
    
    # 初始化数据
    else:
        
        # 获取数据
        if freq is None:
            data = ts.pro_bar(ts_code=ts_code, adj=adj)
        else:
            data = ts.pro_bar(ts_code=ts_code, adj=adj, freq=freq)

        data = data.sort_values(by="trade_date").reset_index(drop=True)

        update = False

        # 计算 macd
        data = cal_macd(data, update)
    
    # 保存数据
    data.to_csv((root_dir), index=False)
            