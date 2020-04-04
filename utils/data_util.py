import tushare as ts
import numpy as np
import pandas as pd
import time
import os

import sys
sys.path.append("../utils/")
import token_util
import date_util

from jqdatasdk import *
auth('15211097884','097884')

pro = token_util.set_token()

def get_stock_list(month_before=12, delta_price=None, total_mv=100):
    
    """
    month_before : 获取n个月之前所有上市公司的股票列表，
                    默认为获取一年前上市公司股票列表
    delta_price ：用于剔除掉金额大于delta_price的股票，若为空则不剔除
    
    
    TIPS : delta_price 和今天的股价进行比较 
    """
    trade_date = date_util.get_current_date()
    
    stock_list = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name,market,list_date')
    
    # 去除创业板和科创板股票
    stock_list1 = stock_list[~stock_list['market'].isin(["科创板"])].reset_index(drop=True)
    
    # 去除ST，银行，证券和国企的股票
    index_list = []
    for i in range(len(stock_list1)):
        if '银行' in stock_list1.iloc[i]['name'] \
            or 'ST' in stock_list1.iloc[i]['name'] \
                or '证券' in stock_list1.iloc[i]['name'] \
                    or '中' in stock_list1.iloc[i]['name'] \
                        or '国' in stock_list1.iloc[i]['name'] :
                            index_list.append(i)
                
    for i in index_list:
        stock_list1 = stock_list1.drop(i)
    
    stock_list1 = stock_list1.reset_index(drop=True)
    
    # 去除一年内上市的股票(默认)
    delta_date = date_util.get_date_months_before(month_before)
    stock_list2 = stock_list1[stock_list1["list_date"] <= delta_date].reset_index(drop=True)

    stock_list = stock_list2.drop(['market', 'list_date'], axis=1)
    
    # 剔除 date_time 时刻价格高于delta_price的股票
    if delta_price is not None:
        
        stock_list['price'] = np.zeros(len(stock_list))
        
        for i in range(len(stock_list)):
            stock_code = stock_list.iloc[i]["ts_code"]
            try:
                current_df = ts.pro_bar(ts_code=stock_code, adj='qfq',
                                        start_date=trade_date, end_date=trade_date)
                if current_df.empty:
                    continue
                stock_list.loc[i, "price"] = (current_df.loc[0, "close"] + current_df.loc[0, "pre_close"]) / 2

            except:
                time.sleep(3)
            
        stock_list = stock_list[stock_list["price"] <= delta_price]
    
    # 去除市值在x亿之下的公司
    if total_mv is not None:
        for i in range(len(stock_list)):

            try:

                df = pro.daily_basic(ts_code=stock_list["ts_code"][i], \
                                     trade_date=trade_date, fields='ts_code,total_mv')
                stock_list.loc[i, "total_mv"] = df.loc[0, "total_mv"] if df.empty is False else 0

            except:
                time.sleep(3)

        stock_list = stock_list[stock_list["total_mv"] > total_mv * 10000].reset_index(drop=True)
    
    stock_list.to_csv("./data_pulled/stock_date_delta_price{}.csv".format(delta_price), index=False)
    
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
        freq = "D"
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
            
            data_tmp = ts.pro_bar(ts_code=ts_code, adj=adj, start_date=start_date, end_date=end_date, freq=freq)
            
            # 针对周k不需要更新的情况
            if data_tmp is None:
                return
            
            data_tmp = data_tmp.sort_values(by="trade_date").reset_index(drop=True)
            
            # 在 data_tmp中构造data中所有的列，以便和data合并
            for column in data.columns:
                if column not in data_tmp.columns:
                    data_tmp[column] = data_tmp["change"]
            
            # 将data的最后一行数据插入到data_tmp中，以便计算macd,dif,eda
            data_last = pd.DataFrame(np.array(data.iloc[-1]).reshape(1,-1), columns=data_tmp.columns)
            data_tmp = pd.concat([data_last, data_tmp], sort=True).reset_index(drop=True)
            
            # 计算结果并和data合并
            data_tmp = cal_macd(data_tmp, update)
            data = pd.concat([data, data_tmp.drop(0)], sort=True)
    
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
    data.to_csv(root_dir, index=False)
    
def get_industry_concept(industry_list, concept_list):
    
    stock_list = []

    for concept in concept_list:
        stocks = get_concept_stocks(concept, date='2019-11-11')
        for i in stocks:
            if i[7:] == "XSHE" :
                stock_list.append(i[:6] + ".SZ")
            else:
                stock_list.append(i[:6] + ".SH")

    for industry in industry_list:
        stocks = get_industry_stocks(industry, date='2019-11-11')
        for i in stocks:
            if i[7:] == "XSHE" :
                stock_list.append(i[:6] + ".SZ")
            else:
                stock_list.append(i[:6] + ".SH")
    
    return stock_list

def pull_holder_num(ts_code, root_dir):
    
    root_dir = os.path.join(root_dir, "holder_num")
    root_dir = os.path.join(root_dir, "{}.csv".format(ts_code))
    
    end_date = date_util.get_current_date()
    
    data = pro.stk_holdernumber(ts_code=ts_code, end_date=end_date)
    
    data.to_csv(root_dir, index=False)