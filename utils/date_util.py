from datetime import datetime
from datetime import timedelta
import pandas as pd

def add_zero(date):
    
    nabs = abs(int(date))
    return str(nabs) if nabs>=10 else "0" + str(nabs)

def get_datetime_object(date):
    
    if date is None:
        date = datetime.now()
        
    else:
        year = int(date[:4])
        month = int(date[4:6])
        day = int(date[6:])
        
        date = datetime(year, month, day)
    
    return date

def get_date_months_before(month_n, year_n=0, date=None):
    
    """Return the date months and years ago of current date.
    
    Args:
        month_n: A int variable
        year_n: A optional int variable
    
    Returns:
        A string of the date.
        For example:
        
        get_date_months_before(3)
        >>> '20190801'
        
    """
    
    date = get_datetime_object(date)
    
    this_year = date.year
    this_month = date.month
    this_day = date.day if date.day <= 28 else 28
    
    total_month = this_month - (year_n * 12 + month_n)
    
    if 0 < total_month < 12: 
        total_month = add_zero(total_month)
        return str(this_year) + total_month + str(this_day)
    else: 
        i = total_month // 12 
        j = total_month % 12 
        if j == 0: 
            i -= 1 
            j = 12 
        this_year += i 
        j = add_zero(j) 
        return str(this_year) + str(j) + str(this_day)

def get_date_weeks_before(week_n, date=None):
    
    date = get_datetime_object(date)
    days = timedelta(days = 7 * week_n)
    dayfrom = date - days
    
    return tramsform_datetime_to_str(dayfrom)
    
    
def get_next_n_day(date=None, n_day=5):
    
    """Return the date next n days.
    
    Args:
        date: current date
        n_day: the num of days you want to get.
    
    Returns:
        A string of the date.
        For example:
        
        get_next_n_day('20190801', 3)
        >>> '20190804'
        
    """
    
    date = get_datetime_object(date)
    
    next_date = date + timedelta(days=n)
    
    return tramsform_datetime_to_str(date)

def get_work_day_range(start_date, end_date):
    data_tmp = pd.read_csv("../data_pulled/day/000001.SZ.csv")
    
    star_port = data_tmp["trade_date"]>=int(start_date)
    end_port = data_tmp["trade_date"]<int(end_date)
    date_list = data_tmp[star_port & end_port].index.to_list()
    
    work_date_list = data_tmp["trade_date"][date_list].to_list()
    
    return [str(date) for date in work_date_list]

def tramsform_datetime_to_str(date):
    
    this_year = date.year
    this_month = add_zero(date.month)
    this_day = add_zero(date.day)
    
    return str(this_year) + this_month + this_day

def get_current_date():
    
    date = datetime.now()
    
    return tramsform_datetime_to_str(date)
    