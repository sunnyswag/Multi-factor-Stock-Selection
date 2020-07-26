# Multi-factor Stock Selection

计划你的交易，交易你的计划

## Introduction

这是关于**多因子选股**的项目，~~自动交易部分已经archive~~

交易前期(1-3年)具有参考价值，有需要的朋友可以自取。

不过，个人看来，这是在自己投资交易前期，为了感动自己所做的一些工作。

不做不知道，做完才可以决定将这条路pass掉

近期交易策略 [在此](http://note.youdao.com/noteshare?id=3f34f9c3cceddd406fe18dc218f061ce&sub=5B475C8834D34C269472DCDA56B18710) 查看

**这个世界不存在取款机**，也不缺少幻想着取款机的傻瓜

## Getting Started

没用到 ml && dl ，仅仅通过逻辑判断选股

### Requirements

1. tushare ：主要的数据获取平台，需要注册账号并获取tushare码
2. joinquant ：数据非常全面，不过很多都用不到，同样需要进行注册
3. python
4. jupyter-lab：编辑器。如何使用请自行学习

### Installation

1. 下载依赖包

   ```
   pip install -r requirements.txt
   ```

2. 打开 [./utils/token_util.py](./utils/token_util.py) 更换tushare码
3. 打开并运行[./pull_data.ipynb](./pull_data.ipynb) ，会自动新建 ```./data_pulled``` 文件夹，并将爬取好的股票数据储存在该文件夹下
4. 打开 [/test](/test) 文件夹运行你想获取的数据

## Future Work

以后大概率不会进行更新了，有需要的朋友可以自取

通过多因子选股，找到的肯定是处在上升周期的公司。那么这些公司的上升阶段还会持续，抑或是已经结束了呢？

更多的精力应该放到行业及公司的研究上，周期的波谷，往往是最佳的布局时机。而这，多因子选股无法做到

