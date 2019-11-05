import token_util
import date_util
import tushare as ts
import numpy as np



# def cal_ma(ts_code, start_date=None, end_date=None, short_=7, long_=14, pct_chg_short=3, pct_chg_long=5, adj='qfq'):
    
#     if end_date is None:
#         end_date = date_util.get_current_date()
    
#     if start_date is None:
#         data = ts.pro_bar(ts_code=ts_code, end_date=end_date, ma=[short_, long_], adj=adj)
#     else:
#         data = ts.pro_bar(ts_code=ts_code, start_date=start_date, end_date=end_date, ma=[short_, long_], adj=adj)
    
#     ma7_1, ma7_2 = data.loc[1, "ma{}".format(short_)], data.loc[0, "ma{}".format(short_)]
#     ma14_1, ma14_2 = data.loc[1, "ma{}".format(long_)], data.loc[0, "ma{}".format(long_)]
    
#     amount_mean = data["amount"].mean()
#     ptc_chg_short = data["pct_chg"][:pct_chg_short].sum()
    
#     return ma7_1, ma7_2, ma14_1, ma14_2, amount_mean, ptc_chg_short

def negetive_macd_judge(data_macd):
    
    negetive_macd_list = []
    for i in reversed(range(len(data_macd))):
        if data_macd.iloc[i] < 0:
            negetive_macd_list.append(data_macd.iloc[i])
        else:
            break
    
    average_macd = np.array(negetive_macd_list).mean()
    
    return True if average_macd < data_macd.iloc[-1] else False