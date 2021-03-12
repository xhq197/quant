#  -*- coding: utf-8 -*-


import traceback
from pandas.io import json
from pymongo import UpdateOne

from database import DB_CONN
from stock_util import get_all_codes
import baostock as bs
import  pandas as pd


"""
从tushare获取股票基础数据，保存到本地的MongoDB数据库中
"""


def crawl_basic():
    """
    抓取所有股票的股票基础信息
    """

    # 获取指定日期范围的所有交易日列表
    all_codes = get_all_codes()

    # 按照每个交易日抓取

    lg = bs.login()
    for code in all_codes:
        try:
            # 抓取当日的基本信息
            crawl_basic_at_code(code)
        except:
            print('抓取股票基本信息时出错，代码：%s' % code, flush=True)
    bs.logout()


def crawl_basic_at_code(code):
    """
    从Tushare抓取指定代码的股票基本信息
    :param code: 股票代码
    """
    # 从baostock获取基本信息
    # 获取证券基本资料
    if code[0] == '6':
        code1 = "sh." + str(code)
    else:
        code1 = "sz." + str(code)
    rs = bs.query_stock_basic(code=code1)
    # 打印结果集
    # data_list = []
    # while (rs.error_code == '0') & rs.next():
    #     # 获取一条记录，将记录合并在一起
    #     data_list.append(rs.get_row_data())
    # df_basics = pd.DataFrame(data_list, columns=rs.fields)
    # df_basics = pd.DataFrame(rs.get_row_data(), columns=rs.fields)
    fields = rs.fields
    row_data = rs.get_row_data()
    dict_basics = {}
    for i,field in enumerate(fields):
        dict_basics[field] = row_data[i]

    # 如果某股票没有基础信息，在不做操作
    if dict_basics is None:
        print(code,'无基本信息')
        return

    if  len(dict_basics) != 6:
        print(code,'基本信息有误','\n',dict_basics)
        return

    try:
        # 初始化更新请求列表
        update_requests = []
        doc = dict_basics
        doc['code'] = doc['code'][3:]
        # print(doc)
        # print(json.loads(json.dumps(doc)))
        # 生成更新请求，需要按照code和date创建索引
        # tushare
        # numpy.int64/numpy.float64等数据类型，保存到mongodb时无法序列化。
        # 解决办法：这里使用pandas.json强制转换成json字符串，然后再转换成dict。int64/float64转换成int,float
        update_requests.append(
            UpdateOne(
                {'code': code},
                {'$set': doc}, upsert=True))
    except:
        print('发生异常，股票代码：%s' % (code), flush=True)
        print(doc, flush=True)
        print(traceback.print_exc())

    # 如果抓到了数据
    if len(update_requests) > 0:
        update_result = DB_CONN['basic'].bulk_write(update_requests, ordered=False)

        print('抓取股票基本信息，代码：%s, 插入：%4d条，更新：%4d条' %
              (code, update_result.upserted_count, update_result.modified_count), flush=True)


if __name__ == '__main__':
    crawl_basic()