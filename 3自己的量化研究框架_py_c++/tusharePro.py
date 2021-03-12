import tushare as ts
from datetime import datetime
from stock_util import get_trading_dates,get_all_codes

def get_trade_days(begin_date = '2001-08-27',end_date = None):
    if(end_date is None):
        end_date = datetime.now().strftime('%Y-%m-%d')
    alldays = ts.get_k_data('600519', autype=None, start=begin_date, end=end_date).date
    return alldays.tolist()

def get_last_trade_day(date): #'%Y-%m-%d'
    tradingdays_list = get_trade_days()
    if date in tradingdays_list:
        today_index  = tradingdays_list.index(date)
        return tradingdays_list[int(today_index)-1]

def get_next_trade_day(date): #'%Y-%m-%d'
    tradingdays_list = get_trade_days()
    if date in tradingdays_list:
        today_index  = tradingdays_list.index(date)
        if(today_index == len(tradingdays_list) -1):
            return -1
        return tradingdays_list[int(today_index)+1]




def get_tushare_code(begin_date = '2000-01-01',end_date = None):
    if(end_date is None):
        end_date = datetime.now().strftime('%Y-%m-%d')
    # 初始化pro接口
    pro = ts.pro_api('f3ef4ac4dc04104e0573aa75c29aef70f30837a416baf6cd1a0f8e81')
    tradingdays_list = get_trading_dates(begin_date= begin_date,end_date = end_date)
    # tradingdays_list = get_trade_days(begin_date= begin_date,end_date = end_date)
    codes = set()
    for day in tradingdays_list:
        data = pro.daily(trade_date = day.replace('-',''))
        codes = codes | set(data.ts_code)
    return list(codes).sort()

if __name__ == '__main__':
    # print(get_tushare_code(begin_date = '2015-01-01',end_date = None))
    print(len(get_all_codes()))


