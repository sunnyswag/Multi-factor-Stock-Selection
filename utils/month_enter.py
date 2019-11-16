import date_util
import pandas as pd
import numpy as np
import time
import os

def get_start_stock(trade_date=None, stock_list_dir=None):
    
    stock_list_result = []
    
    if trade_date is None:
        trade_date = date_util.get_current_date()
    elif len(trade_date) != 8:
        return "please check the date format. for example, \'20191010\'"
    
    if stock_list_dir is None:
        stock_list_dir = "../data_pulled/stock_date_2018119_delta_priceNone.csv"
        
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
            
            cur_dif = cur_detail.iloc[cur_index]["diff"]
            cur_dea = cur_detail.iloc[cur_index]["dea"]
            
            if cur_macd > 0 and last_macd < 0 :
                 if cur_dif > 0 and cur_dea > 0 :
                    stock_list_result.append(stock_code)
        
    return stock_list_result

def get_secure_stock(trade_date=None, stock_list_dir=None, month_num=2):
    
    stock_list_result = []
    
    if trade_date is None:
        trade_date = date_util.get_current_date()
    elif len(trade_date) != 8:
        return "please check the date format. for example, \'20191010\'"
    
    if stock_list_dir is None:
        stock_list_dir = "../data_pulled/stock_date_2018119_delta_priceNone.csv"
        
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
            
            cur_dif = cur_detail.iloc[cur_index]["diff"]
            cur_dea = cur_detail.iloc[cur_index]["dea"]
            
            last_dif = cur_detail.iloc[cur_index-1]["diff"]
            last_dea = cur_detail.iloc[cur_index-1]["dea"]
            
            if month_num == 2 :
                macd_true = cur_macd > 0 and last_macd > 0
                dea_dif_ture = cur_dif>0 and cur_dea>0 and last_dif>0 and last_dea>0
            elif month_num == 3 :
                llast_macd = cur_detail.iloc[cur_index-2]["macd"]
                llast_dif = cur_detail.iloc[cur_index-2]["diff"]
                llast_dea = cur_detail.iloc[cur_index-2]["dea"]
                macd_true = cur_macd > 0 and last_macd > 0 and llast_macd > 0
                dea_dif_ture = cur_dif>0 and cur_dea>0 and last_dif>0 and last_dea>0 and llast_dif>0 and llast_dea>0
            
            if macd_true and dea_dif_ture and cur_macd > last_macd:
                stock_list_result.append(stock_code)
        
    return stock_list_result