import token_util
import date_util
import tushare as ts
import pandas as pd
import numpy as np
import os

def get_condidate_stock(trade_date=None):
    
    if trade_date is None:
        trade_date = date_util.get_current_date()
    
    stock_list = pd.read_csv("../data_pulled/stock_list.csv")
    
    columns = ["stock_code", "name", "pct_chg_short", "his_macd_discount", "amount_mean_20", "amount_discount_mean"]
    raw_choose_list = pd.DataFrame(columns = columns)

    ROOT_PATH = os.path.join("..", "data_pulled")
    ROOT_PATH = os.path.join(ROOT_PATH, "day")
    stock_csv_list = os.listdir(ROOT_PATH)
    
    # 若第一个文件为 '.ipynb_checkpoints'
    num = 1 if stock_csv_list[0] == '.ipynb_checkpoints' else 0
    
    for i in range(len(stock_list)):

        stock_code = stock_list.iloc[i]["ts_code"]
        name = stock_list.iloc[i]["name"]

        if stock_code + ".csv" == stock_csv_list[i+num]:
            cur_detail = pd.read_csv(os.path.join(ROOT_PATH, stock_csv_list[i+num]))
            cur_index = cur_detail[cur_detail["trade_date"] == int(trade_date)].index.tolist()

            # 若此股票此时还未上市，则跳过
            if cur_index == []:
                continue
            else:
                cur_index = cur_index[0]

            cur_macd = cur_detail.iloc[cur_index]["macd"]
            last_macd =  cur_detail.iloc[cur_index-1]["macd"]
            cur_dif = cur_detail.iloc[cur_index]["diff"]
            cur_dea = cur_detail.iloc[cur_index]["dea"]
            pos_dif_mean = cur_detail["diff"][cur_detail["diff"] > 0].mean()
            pos_dea_mean = cur_detail["dea"][cur_detail["dea"] > 0].mean()

            # (最近3天涨跌幅).sum()
            ptc_chg_short = cur_detail["pct_chg"][cur_index-2:cur_index+1].sum()

            # 历史数据(MACD>0)天数 / 总的天数
            data_macd = cur_detail["macd"][:cur_index+1]
            his_macd_discount = len(data_macd[data_macd > 0]) / len(data_macd)

            # 近一个月成交量均值 / 近两个月成交量均值
            amount_mean_20 = cur_detail["amount"][cur_index - 20:cur_index].mean()
            amount_mean_40 = cur_detail["amount"][cur_index - 40:cur_index].mean()
            amount_discount_mean = amount_mean_20 / amount_mean_40

            # 判断 macd：今天 > 0, 昨天 < 0
            if cur_macd > 0 and last_macd < 0:
                # 判断今天的 dif 是否比 dea大
                if cur_dif - cur_dea > 0.001:
                    # 判断 dif 和 dea 是否大于0，且小于正dif/dea的平均值
                    if 0 < cur_dif < pos_dif_mean and 0 < cur_dea < pos_dea_mean:
                        list_tmp = pd.DataFrame([[stock_code, name, ptc_chg_short, his_macd_discount,
                                                  amount_mean_20, amount_discount_mean]], columns=columns)
                        raw_choose_list = raw_choose_list.append(list_tmp)
                    
    # 数据归一化

    choose_list = raw_choose_list

    for column in choose_list.columns[2:]:
        c_data = choose_list[column]
        choose_list[column] = (c_data-c_data.mean()) / c_data.std()

    # 排序

    def get_rank_factor(arr):
        pct_chg_short = arr["pct_chg_short"] * 0.5
        his_macd_discount = arr["his_macd_discount"]
        amount_mean_20 = arr["amount_mean_20"] * 0.5
        amount_discount_mean = arr["amount_discount_mean"] * 0.5
        return pct_chg_short+his_macd_discount+amount_mean_20+amount_discount_mean

    choose_list["rank_factor"] = choose_list.apply(get_rank_factor, axis = 1)
    choose_list = choose_list.sort_values(by="rank_factor", ascending= False).reset_index(drop=True)
    
    return choose_list

def negetive_macd_judge(data_macd):
    
    negetive_macd_list = []
    for i in reversed(range(len(data_macd))):
        if data_macd.iloc[i] < 0:
            negetive_macd_list.append(data_macd.iloc[i])
        else:
            break
    
    average_macd = np.array(negetive_macd_list).mean()
    
    return True if average_macd < data_macd.iloc[-1] else False