#  -*- coding: utf-8 -*-

"""
普量学院量化投资课程系列案例源码包
普量学院版权所有
仅用于教学目的，严禁转发和用于盈利目的，违者必究
©Plouto-Quants All Rights Reserved

普量学院助教微信：niuxiaomi3
"""

from pymongo import ASCENDING
from database import DB_CONN
from datetime import datetime, timedelta
import tushare as ts


def get_trading_dates(begin_date=None, end_date=None):
    """
    获取指定日期范围的按照正序排列的交易日列表
    如果没有指定日期范围，则获取从当期日期向前365个自然日内的所有交易日

    :param begin_date: 开始日期
    :param end_date: 结束日期
    :return: 日期列表
    """

    # 当前日期
    now = datetime.now()
    # 开始日期，默认今天向前的365个自然日
    if begin_date is None:
        # 当前日期减去365天
        one_year_ago = now - timedelta(days=365)
        # 转化为str类型
        begin_date = one_year_ago.strftime('%Y-%m-%d')

    # 结束日期默认为今天
    if end_date is None:
        end_date = now.strftime('%Y-%m-%d')

    # 用上证综指000001作为查询条件，因为指数是不会停牌的，所以可以查询到所有的交易日
    daily_cursor = DB_CONN.daily.find(
        {'code': '000001', 'date': {'$gte': begin_date, '$lte': end_date}, 'index': True},
        sort=[('date', ASCENDING)],
        projection={'date': True, '_id': False})
    #筛选条件：{'code': '000001', 'date': {'$gte': begin_date, '$lte': end_date}, 'index': True}
    #排序： sort=[('date', ASCENDING)]
    #查询内容：projection={'date': True, '_id': False})

    # 转换为日期列表
    dates = [x['date'] for x in daily_cursor]

    return dates


def get_all_codes(type =1):
    """
    获取所有股票代码列表

    :return: 股票代码列表
    """
    if(type == 1):
        # 通过distinct函数拿到所有不重复的股票代码列表
        # return DB_CONN.basic.distinct('code') #basic为空表，改成daily
        return DB_CONN.daily.distinct('code')
    elif(type == 2):
        pro = ts.pro_api('f3ef4ac4dc04104e0573aa75c29aef70f30837a416baf6cd1a0f8e81')
        end_date = datetime.now().strftime('%Y-%m-%d')
        codes_data = pro.daily(trade_data=end_date.replace('-', '')).ts_code
        codes_data = list(set(codes_data.to_list()))
        codes = [code[:6] for code in codes_data]
        codes.sort(reverse=False)
        return codes




if __name__ == '__main__':
    get_all_codes()
