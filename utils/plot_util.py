import math
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def plot(data, golden_port):
    
    plt.figure(figsize=(20,10))
    columns = 8
    rows = math.ceil(len(golden_port['index']) / columns)
    
    enter_true, enter_false = [], []
    num_plot = 1
    
    for i in range(rows):
        for j in range(columns):
            
            # 本行的图已画完
            if num_plot > len(golden_port['index']):
                break
            
            # 获取data中的当前索引
            index = golden_port['index'][num_plot-1]
            
            # 数据缺失
            if (index + 11) > len(data):
                break
            
            # 如果8天之后ema7还在ema4上方，则表示正确入场，否则表示错误入场
            if data["ema7"][index+8] > data["ema14"][index+8]:
                current_enter = "True"
                enter_true.append(golden_port['date'][num_plot-1])
            else:
                current_enter = "False"
                enter_false.append(golden_port['date'][num_plot-1])
            
            plt.subplot(rows, columns, num_plot)
            plt.title(str(index) + " " + golden_port['date'][num_plot-1] + " " + current_enter)
            plt.plot(data["ema7"][index:index + 10])
            plt.plot(data["ema14"][index:index + 10])
            plt.axis("off")
            num_plot += 1
    
    plt.show()
    
    enter_discount = len(enter_true) / (len(enter_true)+len(enter_false))
    
    return enter_true, enter_false, enter_discount