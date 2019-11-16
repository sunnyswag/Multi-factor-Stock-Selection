import date_util
import pandas as pd
import numpy as np
import time
import os

def get_declining_stock(trade_date=None, times = 2, stock_list_dir=None, ready=False):
    
    middle_year = 120
    
    stock_list_result = []
    
    if trade_date is None:
        trade_date = date_util.get_current_date()
    elif len(trade_date) != 8:
        return "please check the date format. for example, \'20191010\'"
    
    if stock_list_dir is None:
        stock_list_dir = "../data_pulled/stock_date_2018119_delta_priceNone.csv"
        
    stock_list = pd.read_csv(stock_list_dir)
    
    ROOT_PATH = os.path.join("..", "data_pulled")
    ROOT_PATH = os.path.join(ROOT_PATH, "day")
    stock_csv_list = os.listdir(ROOT_PATH)
    
    # 若第一个文件为 '.ipynb_checkpoints'
    num = 1 if stock_csv_list[0] == '.ipynb_checkpoints' else 0
    
    for i in range(len(stock_list)):
        
        stock_code = stock_list.iloc[i]["ts_code"]
        name = stock_list.iloc[i]["name"]
        
        if stock_code + '.csv' in stock_csv_list:
            stock_csv_list_index = stock_csv_list.index(stock_code + '.csv')
            cur_detail = pd.read_csv(os.path.join(ROOT_PATH, stock_csv_list[stock_csv_list_index]))
            cur_index = cur_detail[cur_detail["trade_date"] == int(trade_date)].index.tolist()

            # 若此股票此时还未上市，则跳过
            if cur_index == []:
                continue
            else:
                cur_index = cur_index[0]
            
            
            if cur_index - middle_year * times > middle_year * times :
                
                cur_close = cur_detail["close"][cur_index]
                pre_close = cur_detail["close"][cur_index - middle_year * times]
                ptc_change = abs((pre_close - cur_close) / pre_close)
                
                cur_ema26 = cur_detail["ema26"][cur_index]
                pre_ema26 = cur_detail["ema26"][cur_index - middle_year * times]
                ema_change = abs(cur_ema26 - pre_ema26)
                
                if ema_change < 1.5 and ptc_change < 0.15 :
                    if ready:
                        
                        pre_max_close = cur_detail["close"][cur_index - int(middle_year * times / 2)-10 : cur_index-10].max()
                        
                        if cur_close >= pre_max_close :
                            stock_list_result.append(stock_code)
                            
                    else:
                        stock_list_result.append(stock_code)
        
    return stock_list_result