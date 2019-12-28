import date_util
import pandas as pd
import numpy as np
import time
import os
from jqdatasdk import *
auth('15211097884','097884')

def query_stock(stock_code):

    q = query(
          income.statDate,
          indicator.roe, # 股东权益报酬率(%) RoE
          indicator.roa, # 总资产报酬率(%) RoA
      ).filter(
          income.code == stock_code
      )
    
    return q

def ts_code_trans(ts_code):
    if ts_code[7:] == "SZ" :
        return ts_code[:6] + ".XSHE"
    else:
        return ts_code[:6] + ".XSHG"

def get_start_stock(trade_date=None, stock_list_dir=None):
    
    stock_list_result = []
    
    if trade_date is None:
        trade_date = date_util.get_current_date()
    elif len(trade_date) != 8:
        return "please check the date format. for example, \'20191010\'"
    
    if stock_list_dir is None:
        stock_list_dir = "../data_pulled/stock_date_delta_priceNone.csv"
        
    stock_list = pd.read_csv(stock_list_dir)
    
    ROOT_PATH = os.path.join("..", "data_pulled")
    ROOT_PATH = os.path.join(ROOT_PATH, "month")
    stock_csv_list = os.listdir(ROOT_PATH)
    
    # 若第一个文件为 '.ipynb_checkpoints'
    num = 1 if stock_csv_list[0] == '.ipynb_checkpoints' else 0
    
    for i in range(len(stock_list)):
        
        stock_code = stock_list.iloc[i]["ts_code"]
        name = stock_list.iloc[i]["name"]
        
        if stock_code + '.csv' in stock_csv_list:
            stock_csv_list_index = stock_csv_list.index(stock_code + '.csv')
            cur_detail = pd.read_csv(os.path.join(ROOT_PATH, stock_csv_list[stock_csv_list_index]))
            cur_index = cur_detail[cur_detail["trade_date"] <= int(trade_date)].index.tolist()

            # 若此股票此时还未上市，则跳过
            if cur_index == []:
                continue
            else:
                cur_index = cur_index[-1]
            
            # macd and dea condition
            
            cur_macd = cur_detail.iloc[cur_index]["macd"]
            last_macd = cur_detail.iloc[cur_index-1]["macd"]
            llast_macd = cur_detail.iloc[cur_index-2]["macd"]
            
            cur_dea = cur_detail.iloc[cur_index]["dea"]
            last_dea = cur_detail.iloc[cur_index-1]["dea"]
            
            cur_dif = cur_detail.iloc[cur_index]["diff"]
            last_dif = cur_detail.iloc[cur_index - 1]["diff"]
            
            # macd出现反转，dea大于0
            condition1 = cur_dea > 0 and llast_macd > last_macd and last_macd < cur_macd
            # macd持续增长，此时dea开始大于0
            condition2 = cur_macd > last_macd and cur_dea > 0 and last_dea < 0
            # macd出现第一根绿柱，dea大于0
            condition3 = cur_macd > 0 and last_macd < 0 and cur_dea > 0
            
            if cur_dif > last_dif and (condition1 or condition2 or condition3):
                
                # roa and roe condition
            
                q = query_stock(ts_code_trans(stock_code))
                rets = None

                for i in range(4, 9):
                    ret = get_fundamentals(q, statDate='201' + str(i)) 
                    rets = pd.concat([rets, ret], ignore_index=True) if i != 4 else ret
            
                if rets.roa.mean() > 10 and rets.roe.mean() > 10:
                    stock_list_result.append(stock_code)         
        
    return stock_list_result

def get_secure_stock(trade_date=None, stock_list_dir=None):
    
    stock_list_result = []
    
    if trade_date is None:
        trade_date = date_util.get_current_date()
    elif len(trade_date) != 8:
        return "please check the date format. for example, \'20191010\'"
    
    if stock_list_dir is None:
        stock_list_dir = "../data_pulled/stock_date_delta_priceNone.csv"
        
    stock_list = pd.read_csv(stock_list_dir)
    
    ROOT_PATH = os.path.join("..", "data_pulled")
    ROOT_PATH = os.path.join(ROOT_PATH, "month")
    stock_csv_list = os.listdir(ROOT_PATH)
    
    # 若第一个文件为 '.ipynb_checkpoints'
    num = 1 if stock_csv_list[0] == '.ipynb_checkpoints' else 0
    
    for i in range(len(stock_list)):
        
        stock_code = stock_list.iloc[i]["ts_code"]
        name = stock_list.iloc[i]["name"]
        
        if stock_code + '.csv' in stock_csv_list:
            stock_csv_list_index = stock_csv_list.index(stock_code + '.csv')
            cur_detail = pd.read_csv(os.path.join(ROOT_PATH, stock_csv_list[stock_csv_list_index]))
            cur_index = cur_detail[cur_detail["trade_date"] <= int(trade_date)].index.tolist()

            # 若此股票此时还未上市，则跳过
            if cur_index == []:
                continue
            else:
                cur_index = cur_index[-1]
            
            cur_macd = cur_detail.iloc[cur_index]["macd"]
            last_macd = cur_detail.iloc[cur_index-1]["macd"]
            llast_macd = cur_detail.iloc[cur_index-2]["macd"]
            
            cur_dif = cur_detail.iloc[cur_index]["diff"]
            cur_dea = cur_detail.iloc[cur_index]["dea"]
            
            last_dif = cur_detail.iloc[cur_index-1]["diff"]
            last_dea = cur_detail.iloc[cur_index-1]["dea"]
            
            llast_dif = cur_detail.iloc[cur_index-2]["diff"]
            llast_dea = cur_detail.iloc[cur_index-2]["dea"]
            
            cur_ema26 = cur_detail.iloc[cur_index]["ema26"]
            last_ema26 = cur_detail.iloc[cur_index-1]["ema26"]
            llast_ema26 = cur_detail.iloc[cur_index-2]["ema26"]
            
            # macd_true = cur_macd > 0 and last_macd > 0 and llast_macd > 0
            
            macd_true = cur_macd > last_macd and last_macd > llast_macd
            dea_dif_true = cur_dif>0 # and cur_dea>0 and last_dif>0 and last_dea>0 and llast_dif>0 and llast_dea>0
            ema26_true = cur_ema26 > last_ema26 and last_ema26 > llast_ema26
            
            if macd_true and dea_dif_true and ema26_true:
                stock_list_result.append(stock_code)
        
    return stock_list_result