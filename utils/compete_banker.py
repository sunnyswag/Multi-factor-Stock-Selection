import date_util
import pandas as pd
import numpy as np
import time
import os

def get_declining_stock(trade_date=None, 
                        times = 1, 
                        stock_list_dir=None, 
                        ready=True, 
                        ptc_std = 0.1):
    
    middle_year = 120
    
    stock_list_result = []
    
    if trade_date is None:
        trade_date = date_util.get_current_date()
    elif len(trade_date) != 8:
        return "please check the date format. for example, \'20191010\'"
    
    if stock_list_dir is None:
        stock_list_dir = "../data_pulled/stock_date_delta_priceNone.csv"
        
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
                
                # 近段时间在上涨，去除最近十天
                # cur_index = cur_index - 10
                
                cur_close = cur_detail["close"][cur_index]
                middle_close = cur_detail["close"][cur_index - middle_year * times / 2]
                pre_close = cur_detail["close"][cur_index - middle_year * times]
                
                ptc_change = abs((pre_close - cur_close) / pre_close)
                middle_change1 = abs((pre_close - middle_close) / middle_close)
                middle_change2 = abs((middle_close - cur_close) / middle_close)
                
                cur_ema26 = cur_detail["ema26"][cur_index]
                pre_ema26 = cur_detail["ema26"][cur_index - middle_year * times]
                ema_change = abs(cur_ema26 - pre_ema26)
                
                if ema_change < ptc_std * 10 and ptc_change < ptc_std :
                    if middle_change1 < ptc_std and middle_change2 < ptc_std :
                        if ready:

                            # 不考虑最近五天的涨跌
                            pre_max_close = cur_detail["close"][cur_index + 5 - int(middle_year * times / 2)
                                                                : cur_index + 5].max()

                            if cur_detail["close"][cur_index + 10] >= pre_max_close :
                                stock_list_result.append(stock_code)

                        else:
                            stock_list_result.append(stock_code)
        
    return stock_list_result

def get_holder_declining(trade_date, ready=False, stock_list_dir=None):
    
    stock_list_result = []
    
    if trade_date is None:
        trade_date = date_util.get_current_date()
    elif len(trade_date) != 8:
        return "please check the date format. for example, \'20191010\'"
    
    last_date = trade_date[:3] + str(int(trade_date[3])-2) + trade_date[4:]
    
    if stock_list_dir is None:
        stock_list_dir = "../data_pulled/stock_date_delta_priceNone.csv"
        
    stock_list = pd.read_csv(stock_list_dir)
    
    ROOT_PATH = os.path.join("..", "data_pulled")
    ROOT_PATH = os.path.join(ROOT_PATH, "holder_num")
    stock_csv_list = os.listdir(ROOT_PATH)
    
    # 若第一个文件为 '.ipynb_checkpoints'
    num = 1 if stock_csv_list[0] == '.ipynb_checkpoints' else 0
    
    columns = ["stock_code", "name", "score"]
    choose_list = pd.DataFrame(columns = columns)
    
    for i in range(len(stock_list)):
        
        stock_code = stock_list.iloc[i]["ts_code"]
        name = stock_list.iloc[i]["name"]
        
        if stock_code + '.csv' in stock_csv_list:
            stock_csv_list_index = stock_csv_list.index(stock_code + '.csv')
            cur_detail = pd.read_csv(os.path.join(ROOT_PATH, stock_csv_list[stock_csv_list_index]))
            
            # 当前的索引
            cur_index = cur_detail[cur_detail["end_date"] <= int(trade_date)].index.tolist()

            # 若此股票此时还未上市，则跳过
            if cur_index == []:
                continue
            else:
                cur_index = cur_index[0]
                
            # 两年前索引
            last_index  = cur_detail[cur_detail["end_date"] <= int(last_date)].index.tolist()

            # 若此股票此时还未上市，则跳过
            if last_index == []:
                continue
            else:
                last_index = last_index[0]
            
            index_internal = last_index - cur_index
            internal = index_internal // 10
            
            declining = True
            middle_index = index_internal // 2
            score = 0 # 来自于今年decline的百分比和去年decline季度的百分比之和
            
            cur_holder_num = cur_detail["holder_num"][cur_index]
            last_holder_num = cur_detail["holder_num"][last_index]
            
            score = (last_holder_num - cur_holder_num) / last_holder_num
            
            # 整体处于下降状态
            if score > 0:
                if internal <= 1:
                    for i in range(middle_index-1):
                        # 使用两个单位的折扣值，所以是i + 2
                        if cur_detail["holder_num"][i + cur_index] > cur_detail["holder_num"][i + 2 + cur_index]:
                            declining = False
                            break

                    if declining:
                        for i in range(middle_index):
                            cur_tmp = cur_detail["holder_num"][i + cur_index + middle_index]
                            last_tmp = cur_detail["holder_num"][i + 1 + cur_index + middle_index]
                            if cur_tmp < last_tmp :
                                score += (last_tmp - cur_tmp) / last_tmp
                            else:
                                list_tmp = pd.DataFrame([[stock_code, name, score]], columns=columns)
                                choose_list = choose_list.append(list_tmp)  
                                break

                else:
                    # 每隔 internal个间隔计算一次
                    for i in range(middle_index // internal -1):
                        # 使用两个单位的折扣值，所以是i + 2
                        if cur_detail["holder_num"][i*internal + cur_index : (i+1)*internal + cur_index].mean() > \
                            cur_detail["holder_num"][(i+2)*internal + cur_index : (i+3)*internal + cur_index].mean():
                                declining = False
                                break
                    
                    if declining:
                        for i in range(middle_index):
                            cur_tmp = cur_detail["holder_num"][i*internal + cur_index + middle_index: (i+1)*internal + cur_index + middle_index].mean()
                            last_tmp = cur_detail["holder_num"][(i+1)*internal + cur_index + middle_index: (i+2)*internal + cur_index + middle_index].mean()
                            if cur_tmp < last_tmp :
                                score += (last_tmp - cur_tmp) / last_tmp
                            else:
                                list_tmp = pd.DataFrame([[stock_code, name, score]], columns=columns)
                                choose_list = choose_list.append(list_tmp)   
                                break
    
    return choose_list.sort_values(by="score", ascending= False).reset_index(drop=True)        


def get_enter_stock(trade_date=None, stock_list_dir=None):
    
    middle_year = 120
    
    stock_list_result = []
    
    if trade_date is None:
        trade_date = date_util.get_current_date()
    elif len(trade_date) != 8:
        return "please check the date format. for example, \'20191010\'"
    
    if stock_list_dir is None:
        stock_list_dir = "./holder_num.csv"
        
    stock_list = pd.read_csv(stock_list_dir)
    
    ROOT_PATH = os.path.join("..", "data_pulled")
    ROOT_PATH = os.path.join(ROOT_PATH, "day")
    stock_csv_list = os.listdir(ROOT_PATH)
    
    # 若第一个文件为 '.ipynb_checkpoints'
    num = 1 if stock_csv_list[0] == '.ipynb_checkpoints' else 0
    
    for i in range(len(stock_list)):
        
        stock_code = stock_list.iloc[i]["stock_code"]
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
                    
            # 不考虑最近五天的涨跌
#             pre_max_close = cur_detail["close"][cur_index + 5 - int(middle_year / 2)
#                                                                 : cur_index + 5].max()

#             if cur_detail["close"][cur_index] >= pre_max_close :
            if cur_detail["pct_chg"][cur_index] >= 9.5:
                stock_list_result.append(stock_code)
        
    return stock_list_result