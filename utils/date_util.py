from datetime import datetime
from datetime import timedelta

def add_zero(date):
    nabs = abs(int(date))
    return str(nabs) if nabs>=10 else "0" + str(nabs)

def get_date_months_before(month_n, year_n=0):
    
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
    
    date = datetime.now()
    
    this_year = date.year
    this_month = date.month
    this_day = add_zero(1)
    
    total_month = this_month - (year_n * 12 + month_n)
    
    if 0 < total_month < 12: 
        total_month = add_zero(total_month)
        return str(this_year) + total_month + this_day
    else: 
        i = total_month // 12 
        j = total_month % 12 
        if j == 0: 
            i -= 1 
            j = 12 
        this_year += i 
        j = add_zero(j) 
        return str(this_year) + str(j) + this_day
    
def get_next_n_day(date, n_day=5):
    
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
    
    year = int(date[:4])
    month = int(date[4:6])
    day = int(date[6:])
    
    date = datetime(year, month, day)
    
    next_date = date + timedelta(days=n)
    
    year = str(next_date.year)
    month = str(add_zero(next_date.month))
    day = str(add_zero(next_date.day))
    
    return year + month + day