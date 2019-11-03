import tushare as ts

import sys
sys.path.append("../utils/")
import token_util
import date_util

pro = token_util.set_token()

def get_stock_list(trade_date, delta_price=30.0):
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