### 个人觉得具有参考意义的notebook

1、```./select_value_stock_by_net_profit.ipynb``` ：挑选长期成长的价值股。

​		运行后的结果挺令人满意的，但并没有达到我的要求

2、```./send_email.ipynb``` ：我是用这个来进行特殊的提醒，如MA30拐头，等等。

​		具体操作是放到 **joinquant** 上当作策略运行，盘后向我的邮箱发送交易提醒



PS：实际计算的股票较少，这是因为我进行了filter操作，在文件 [../utils/data_util.py](../utils/data_util.py) 的 ```get_stock_list``` 函数中查看到conditions