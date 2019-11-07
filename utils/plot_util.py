import math
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def plot_enter(golden_port, true_port=5, plot_date=False):
    
    """
    golden_port = {"index":[], date":[], "data":[]}
    "index" : (just overlook it)
    "data" : the date of entry.
    "data" : the fast_line and slow_line data after entry of a short period.
    
    true_port : set a check_point to check your entry is true or not.
    
    plot_date : whether you need to set date in subtitle
    """
    
    columns = 8
    rows = math.ceil(len(golden_port['date']) / columns)
    plt.figure(figsize=(columns * 2.5, rows * 2.5))
    
    enter_true, enter_false = [], []
    num_plot = 1
    
    for i in range(rows):
        for j in range(columns):
            
            # 本行的图已画完
            if num_plot > len(golden_port['date']):
                break
            
            # 如果true_port天之后快线还在慢线上方，则表示正确入场，否则表示错误入场
            quick_value = golden_port["data"][num_plot-1].iloc[:,0].values[true_port-1]
            slow_value = golden_port["data"][num_plot-1].iloc[:,1].values[true_port-1]
            if quick_value > slow_value:
                current_enter = "True"
                enter_true.append(golden_port['date'][num_plot-1])
            else:
                current_enter = "False"
                enter_false.append(golden_port['date'][num_plot-1])
            
            plt.subplot(rows, columns, num_plot)
            if plot_date:
                plt.title(str(golden_port['date'][num_plot-1]) + " " + current_enter)
            else:
                plt.title(str(num_plot-1) + "   " + current_enter)
            plt.plot(golden_port["data"][num_plot-1].iloc[:,0].values)
            plt.plot(golden_port["data"][num_plot-1].iloc[:,1].values)
            plt.axis("off")
            num_plot += 1
    
    plt.show()
    
    enter_discount = len(enter_true) / (len(enter_true)+len(enter_false))
    
    return enter_true, enter_false, enter_discount