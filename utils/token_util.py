import tushare as ts

def set_token():
    
    ts.set_token("c3c0813b705e877d3de4e6eed59395edd0825b82f1ef1f5191befc9a")
    # ts.set_token("52d46e61bb5950dc9c538f58f4824625134089e8e8fd987de9e03091")
    pro = ts.pro_api()
    
    return pro