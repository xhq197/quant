#  -*- coding: utf-8 -*-


from pymongo import UpdateOne
from database import DB_CONN
import tushare as ts
from datetime import datetime
from stock_util import get_all_codes
"""
从tushare获取日K数据，保存到本地的MongoDB数据库中
"""


class DailyCrawler:
    def __init__(self):
        """
        初始化
        """

        # 创建daily数据集
        self.daily = DB_CONN['daily']
        print('0',DB_CONN)
        # 创建daily_hfq数据集
        self.daily_hfq = DB_CONN['daily_hfq']

    def crawl_index(self, begin_date=None, end_date=None):
        """
        抓取指数的日K数据。
        指数行情的主要作用：
        1. 用来生成交易日历
        2. 回测时做为收益的对比基准

        :param begin_date: 开始日期
        :param end_date: 结束日期
        """

        # 指定抓取的指数列表，可以增加和改变列表里的值
        index_codes = ['000001', '000300', '399001', '399005', '399006']

        # 当前日期
        now = datetime.now().strftime('%Y-%m-%d')
        # 如果没有指定开始，则默认为当前日期
        if begin_date is None:
            begin_date = now

        # 如果没有指定结束日，则默认为当前日期
        if end_date is None:
            end_date = now

        # 按照指数的代码循环，抓取所有指数信息
        for code in index_codes:
            # 抓取一个指数的在时间区间的数据
            df_daily = ts.get_k_data(code, index=True, start=begin_date, end=end_date)
            print('1',df_daily)
            # 保存数据
            self.save_data(code, df_daily, self.daily, {'index': True})
            print('2', self.save_data)

    def crawl(self, begin_date=None, end_date=None):
        """
        抓取股票的日K数据，主要包含了不复权和后复权两种

        :param begin_date: 开始日期
        :param end_date: 结束日期
        """


        # 当前日期
        now = datetime.now().strftime('%Y-%m-%d')

        # 如果没有指定开始日期，则默认为当前日期
        if begin_date is None:
            begin_date = now

        # 如果没有指定结束日期，则默认为当前日期
        if end_date is None:
            end_date = now

        # 通过tushare的基本信息API，获取所有股票的基本信息
        # stock_df = ts.get_report_data(2020,4)
        # print('3',stock_df)
        # # 将基本信息的索引列表转化为股票代码列表
        # codes = list(stock_df.code)
        ## !!未囊括所有股票代码，从tusharePro下手
        pro = ts.pro_api('f3ef4ac4dc04104e0573aa75c29aef70f30837a416baf6cd1a0f8e81')
        codes_data = pro.daily(trade_data = end_date.replace('-','')).ts_code
        codes_data = list(set(codes_data.to_list()))
        codes = [code[:6] for code in codes_data]
        codes.sort(reverse = False)
        print(len(codes))
        c = 1
        for code in codes:
            print(c,'/',len(codes))
            # 抓取不复权的价格
            df_daily = ts.get_k_data(code, autype=None, start=begin_date, end=end_date)
            self.save_data(code, df_daily, self.daily, {'index': False})

            # 抓取后复权的价格
            df_daily_hfq = ts.get_k_data(code, autype='hfq', start=begin_date, end=end_date)
            self.save_data(code, df_daily_hfq, self.daily_hfq, {'index': False})
            c+= 1

    def save_data(self, code, df_daily, collection, extra_fields=None):
        """
        将从网上抓取的数据保存到本地MongoDB中

        :param code: 股票代码
        :param df_daily: 包含日线数据的DataFrame
        :param collection: 要保存的数据集
        :param extra_fields: 除了K线数据中保存的字段，需要额外保存的字段
        """

        # 数据更新的请求列表
        update_requests = []

        # 将DataFrame中的行情数据，生成更新数据的请求
        for df_index in df_daily.index:
            # 将DataFrame中的一行数据转dict
            doc = dict(df_daily.loc[df_index])
            # 设置股票代码
            doc['code'] = code

            # 如果指定了其他字段，则更新dict
            if extra_fields is not None:
                doc.update(extra_fields)

            # 生成一条数据库的更新请求
            # 注意：
            # 需要在code、date、index三个字段上增加索引，否则随着数据量的增加，
            # 写入速度会变慢，需要创建索引。创建索引需要在MongoDB-shell中执行命令式：
            # db.daily.createIndex({'code':1,'date':1,'index':1},{'background':true})
            # db.daily_hfq.createIndex({'code':1,'date':1,'index':1},{'background':true})
            #Updataone:先查询{'code': doc['code'], 'date': doc['date'], 'index': doc['index']}，如果存在更改为{'$set': doc}
            #若不存在，插入{'$set': doc}，由于频繁查找，所以建议如上文注释创造索引
            update_requests.append(
                UpdateOne(
                    {'code': doc['code'], 'date': doc['date'], 'index': doc['index']},
                    {'$set': doc},
                    upsert=True)
            )
        # 如果写入的请求列表不为空，则保存都数据库中
        if len(update_requests) > 0:
            # 批量写入到数据库中，批量写入可以降低网络IO，提高速度（只需要打开关闭数据库一次）
            update_result = collection.bulk_write(update_requests, ordered=False)
            print('保存日线数据，代码： %s, 插入：%4d条, 更新：%4d条' %
                  (code, update_result.upserted_count, update_result.modified_count),
                  flush=True)


# 抓取程序的入口函数
if __name__ == '__main__':
    dc = DailyCrawler()
    # 抓取指定日期范围的指数日行情
    # 这两个参数可以根据需求改变，时间范围越长，抓取时花费的时间就会越长
    #指数行情数据
    dc.crawl_index('2020-02-23')
    # 抓取指定日期范围的股票日行情
    # 这两个参数可以根据需求改变，时间范围越长，抓取时花费的时间就会越长
    #股票历史数据
    #begin_date > 2001年8月27日 (茅台上市时间)
    # dc.crawl('2015-01-01', '2020-12-31')

    # dc.crawl_index('2015-01-01')
    dc.crawl('2020-02-23')
