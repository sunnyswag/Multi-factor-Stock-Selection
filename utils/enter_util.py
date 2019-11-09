import token_util
import date_util
import tushare as ts
import pandas as pd
import numpy as np
import time
import os

pro = token_util.set_token()

def get_weekk_condidate_stock(trade_date=None, stock_list_dir=None):
    
    if trade_date is None:
        trade_date = date_util.get_current_date()
    elif len(trade_date) != 8:
        return "please check the date format. for example, \'20191010\'"
    
    if stock_list_dir is None:
        stock_list_dir = "../data_pulled/stock_date_20181109_delta_priceNone.csv"
    
    stock_list = pd.read_csv(stock_list_dir)
    
    raw_choose = {"name":[], "stock_code":[], "dif_dea":[]}
    
    ROOT_PATH = os.path.join("..", "data_pulled")
    ROOT_PATH = os.path.join(ROOT_PATH, "week")
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
            
            dif_dea_mean = (abs(cur_dif - cur_dea) + abs(last_dif - last_dea)) / 2
            
            if cur_macd - last_macd > -0.001 and ( cur_dif - last_dif > -0.001 and cur_dea - last_dea > -0.001):
            
                raw_choose["name"].append(name)
                raw_choose["stock_code"].append(stock_code)
                raw_choose["dif_dea"].append(dif_dea_mean)
                
    return trade_date, raw_choose

def get_condidate_stock(trade_date=None, raw_choose=None, use_re_max_min=False):
    
    if trade_date is None:
        trade_date = date_util.get_current_date()
    elif len(trade_date) != 8:
        return "please check the date format. for example, \'20191010\'"
    if type(raw_choose) is not dict:
        return "pelase define the right raw_choose(dict), raw_choose = {\"name\":[], \"stock_code\":[]}"
    
    columns = ["index", "stock_code", "trade_date", "name", "dif_dea", "dif_dea_0", "revenue_mean", "vol_mean_20", "vol_discount_mean"]
    raw_choose_list = pd.DataFrame(columns = columns)
    
    ROOT_PATH = os.path.join("..", "data_pulled")
    ROOT_PATH = os.path.join(ROOT_PATH, "day")
    stock_csv_list = os.listdir(ROOT_PATH)
    
    # 若第一个文件为 '.ipynb_checkpoints'
    num = 1 if stock_csv_list[0] == '.ipynb_checkpoints' else 0
    
    for i in range(len(raw_choose["stock_code"])):

        stock_code = raw_choose["stock_code"][i]
        name = raw_choose["name"][i]
        
        if stock_code + '.csv' in stock_csv_list:
            stock_csv_list_index = stock_csv_list.index(stock_code + '.csv')
            cur_detail = pd.read_csv(os.path.join(ROOT_PATH, stock_csv_list[stock_csv_list_index]))
            cur_index = cur_detail[cur_detail["trade_date"] == int(trade_date)].index.tolist()

            # 若此股票此时还未上市，则跳过
            if cur_index == []:
                continue
            else:
                cur_index = cur_index[0]
            
            cur_macd = cur_detail.iloc[cur_index]["macd"]
            last_macd =  cur_detail.iloc[cur_index-1]["macd"]
            llast_macd = cur_detail.iloc[cur_index-2]["macd"]
            
            cur_dif = cur_detail.iloc[cur_index]["diff"]
            cur_dea = cur_detail.iloc[cur_index]["dea"]
            last_dif = cur_detail.iloc[cur_index - 1]["diff"]
            last_dea = cur_detail.iloc[cur_index - 1]["dea"]
            cur_price = cur_detail.iloc[cur_index]["close"]
            last_price = cur_detail.iloc[cur_index]["pre_close"]
            
            cur_dif_dea_mean = (cur_dif + cur_dea) / 2
            last_dif_dea_mean = (last_dif + last_dea) / 2
            dif_dea_0 = (cur_dif_dea_mean / cur_price + last_dif_dea_mean / last_price) / 2

            # 近半个月成交额均值 / 近一个月成交额均值
            vol_mean_10 = cur_detail["vol"][cur_index - 10:cur_index].mean()
            vol_mean_20 = cur_detail["vol"][cur_index - 20:cur_index].mean()
            vol_discount_mean = vol_mean_10 / vol_mean_20
            
            # 周k dif和dea的差值
            dif_dea = raw_choose["dif_dea"][i]
            
            # 上涨过度
            over_rise = cur_detail["pct_chg"][cur_index] < 9.0 and cur_detail["pct_chg"][cur_index-1] < 9.0
            
            condition = False
            
            # macd 刚开始大于0
            if (cur_macd > -0.001 and last_macd < 0) and  over_rise :
                # 判断今天的 dif 是否比 dea大
                if cur_dif - cur_dea > -0.001:
                    # 判断 dif 和 dea 是否大于0
                    if 0 < cur_dif and 0 < cur_dea :
                        condition = True
                        
            if llast_macd > 0 and last_macd > 0 and cur_macd > 0 :
                if llast_macd > last_macd and cur_macd > last_macd :
                    if abs(cur_dif - cur_dea) > abs(last_dif - last_dea):
                        condition = True
            
            # amcd一直大于0，刚开始大于0
            if condition :
                try:
                    # 使用利润表做判断
                    start_date = trade_date[0:3] + str(int(trade_date[3]) - 1) + trade_date[4:]
                    profit_table = pro.income(ts_code=stock_code, start_date=start_date, end_date=trade_date, 
                                    fields='ts_code,f_ann_date,revenue,n_income_attr_p')
                    profit_table = profit_table.drop_duplicates().reset_index(drop=True)[:2]
                            
                    cur_income_attr = profit_table["n_income_attr_p"][0]
                    last_income_attr = profit_table["n_income_attr_p"][1]
                    cur_revenue = profit_table["revenue"][0]
                    last_revenue = profit_table["revenue"][1]
                    revenue_mean_tmp = (cur_revenue + last_revenue) / 2
                            
                    profit_con = cur_income_attr > 0 and last_income_attr > 0 and cur_revenue > last_revenue
                    revenue_mean = (cur_revenue - last_revenue) / revenue_mean_tmp
                            
                except:
                    time.sleep(3)
                            
                if profit_con:
                        
                    list_tmp = pd.DataFrame([[cur_index, stock_code, trade_date, name, dif_dea, dif_dea_0, revenue_mean,
                                                      vol_mean_20, vol_discount_mean]], columns=columns)
                    raw_choose_list = raw_choose_list.append(list_tmp)
    
    choose_list = raw_choose_list.reset_index(drop=True)
    
    if len(choose_list) != 0:
        
        # 去除vol最大最小值
#         if use_re_max_min:
#             if len(choose_list) > 3 :
#                 max_index = choose_list["vol_mean_20"].idxmax()
#                 choose_list = choose_list.drop([max_index], axis=0).reset_index(drop=True)
#             if len(choose_list) > 6 :
#                 min_index = choose_list["vol_mean_20"].idxmin()
#                 choose_list = choose_list.drop([min_index], axis=0).reset_index(drop=True)
        
        # 数据归一化
#         if len(choose_list) != 1:
#             for column in choose_list.columns:
#                 if choose_list[column].dtypes != "object":
#                     c_data = choose_list[column]
#                     choose_list[column] = (c_data-c_data.mean()) / c_data.std()

        # 排序
        
        def get_rank_factor(arr):
            dif_dea = arr["dif_dea"] * 0.3
            revenue_mean = arr["revenue_mean"] * 0.15
            vol_mean_20 = arr["vol_mean_20"] * 0.2
            vol_discount_mean = arr["vol_discount_mean"] * 0.2
            return dif_dea+revenue_mean+vol_mean_20+vol_discount_mean
        
        choose_list["rank_factor"] = choose_list.apply(get_rank_factor, axis = 1)
        choose_list = choose_list.sort_values(by="rank_factor", ascending= False).reset_index(drop=True)

    return choose_list

def enter_for_plot(test_choose_list):
    
    ROOT_PATH = os.path.join("..", "data_pulled")
    ROOT_PATH = os.path.join(ROOT_PATH, "day")
    stock_csv_list = os.listdir(ROOT_PATH)

    choose_data = {"index":[], "date":[], "data":[]}

    for i in range(len(test_choose_list)):
        stock_path = os.path.join(ROOT_PATH, test_choose_list["stock_code"][i] + ".csv")
        file_exist = os.path.exists(stock_path)
        if file_exist :
            cur_detail = pd.read_csv(stock_path)
            cur_index = test_choose_list["index"][i]
            choose_data["index"].append(cur_index)
            choose_data["date"].append(test_choose_list["trade_date"][i])
            choose_data["data"].append(cur_detail.iloc[cur_index:cur_index+10][["ema12", "ema26"]])
    
    return choose_data

def negetive_macd_judge(data_macd):
    
    negetive_macd_list = []
    for i in reversed(range(len(data_macd))):
        if data_macd.iloc[i] < 0:
            negetive_macd_list.append(data_macd.iloc[i])
        else:
            break
    
    average_macd = np.array(negetive_macd_list).mean()
    
    return True if average_macd < data_macd.iloc[-1] else False