# auto_stocken
自动选股，自动交易

## 选股策略(短线)

```python

# 金叉死叉使用ma7和ma14


# 进场:
# 周k 判断
if macd > macd_before:
    加入日k待选池

if MACD刚开始大于0 and dif - dea > 0.001 and 今天和昨天都未涨停:
    if 0 < dif < pos_dif_mean and 0 < dea < pos_dea_mean：
        加入进场池
     
对股票排序()
进场()

def 对股票排序():
    
    周k dif和dea的差值
    历史数据 macd>0 天数 / 总的天数 * 0.2
    近一个月成交额均值 * 0.4
    近半个月成交额均值 / 近一个月成交额均值
    
    
    列归一化再求和    
    
# 出场:
    
    # 方案：使用，前1，前0天平均值进行测试
    
    昨天交易量平均值 = (前天交易量 + 昨天交易量) / 2
    今天交易量平均值 = (昨天交易量 + 今天交易量) / 2
    
    if 涨幅超过 4% or 今天交易量平均值 <= 昨天交易量平均值:
        准备出场()
        
def 准备出场():
    if 明天下跌 < -0.5%(和所盈利的百分比有关):
        出场()
        

# 持仓的数据状态结构

class Deal:
    def __init__(self):
        self.xxx = xxx
        self.stock_log = pd.DataFrame([xxx])

past_deal = [ , dtype=Deal] # 记录已完成的交易
current_deal = [, dtype=Deal] # 记录正在进行的交易
all_stock_log = pd.DataFrame([xxx]) # 记录每支股票的交易


```
1. 使用‘20190830’这天的数据进行尝试，发现符合要求的有87个，按照要求排序后发现前面的效果都非常差
    改进：只取MACD大于0的股票；只提取近3天涨幅并乘上0.5；提取近两周成交量
2. 对不同的股盘分别处理，大股盘，中股盘，小股盘
    
## 选股策略(中线)
    周k入场，日k离场


## 选股策略(长线)


## IDEA
1. MACD和价格有关