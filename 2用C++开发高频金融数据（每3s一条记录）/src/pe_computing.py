#  -*- coding: utf-8 -*-



"""
compute_pe：计算市盈率
"""

from pymongo import DESCENDING, UpdateOne

from database import DB_CONN
from stock_util import get_all_codes
from log import Logger
finance_report_collection = DB_CONN['finance_report']
daily_collection = DB_CONN['daily']

log = Logger("pe_comuting.log")

def compute_pe():
    """
    计算股票在某只的市盈率
    """

    # 获取所有股票
    codes = get_all_codes()

    for code in codes:
        # print('计算市盈率, %s' % code)
        log.write('计算市盈率, %s\n' % code)
        daily_cursor = daily_collection.find(
            {'code': code, 'index': False},
            projection={'close': True, 'date': True})

        update_requests = []
        for daily in daily_cursor:
            _date = daily['date']
            # 找到该股票距离当前日期最近的年报，通过公告日期查询，防止未来函数
            #'$regex' 正则表达式
            finance_report = finance_report_collection.find_one(
                {'code': code, 'report_date': {'$regex': '\d{4}-12-31'}, 'announced_date': {'$lte': _date}},
                sort=[('announced_date', DESCENDING)]
            )

            if finance_report is None:
                continue

            # 计算滚动市盈率并保存到daily_k中
            eps = 0
            if finance_report['eps'] != '-':
                eps = finance_report['eps']

            if eps is None:
                # print(code,'have no eps')
                log.write('%s have no eps\n'% code)
                continue

            # 计算PE
            if eps != 0:
                update_requests.append(UpdateOne(
                    {'code': code, 'date': _date, 'index': False},
                    {'$set': {'pe': round(daily['close'] / eps, 4)}}))

        if len(update_requests) > 0:
            update_result = daily_collection.bulk_write(update_requests, ordered=False)
            log.write('更新PE, %s, 更新：%d\n' % (code, update_result.modified_count))
            # print('更新PE, %s, 更新：%d' % (code, update_result.modified_count))


if __name__ == "__main__":
    compute_pe()
