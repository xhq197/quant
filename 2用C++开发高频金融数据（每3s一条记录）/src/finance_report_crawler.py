#  -*- coding: utf-8 -*-


"""
在东方财富网站上抓取财报数据，主要关注EPS、公告日期、报告期
"""

import json
import urllib3

from pymongo import UpdateOne

from database import DB_CONN
from stock_util import get_all_codes

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'


def crawl_finance_report():
    # 先获取所有的股票列表
    codes = get_all_codes(2)
    # 创建连接池
    conn_pool = urllib3.PoolManager()

    # 抓取的财务地址，scode为股票代码
    # url = 'http://dcfm.eastmoney.com//em_mutisvcexpandinterface/api/js/get?' \
    #       'type=YJBB20_YJBB&token=70f12f2f4f091e459a279469fe49eca5&st=reportdate&sr=-1' \
    #       '&filter=(scode={0})&p={page}&ps={pageSize}&js={"pages":(tp),"data":%20(x)}'
    url = 'http://datacenter.eastmoney.com/api/data/get?callback=jQuery11230813372504046614_' \
          '1613984932139&st=REPORTDATE&sr=-1&ps={pagesize}&p={page}&sty=ALL&filter=(SECURITY_CODE%3D%22{0}%22)' \
          '&token=894050c76af8597a853f5b408b759f5d&type=RPT_LICO_FN_CPD'
    pagesize = '1000' #此时数据只有一页
    page = '1'
    url = url.replace('{pagesize}',pagesize)
    url = url.replace('{page}',page)
    # 循环抓取所有股票的财务信息
    for code in codes:
        # 替换股票代码，抓取该只股票的财务数据
        response = conn_pool.request('GET', url.replace('{0}', code))

        # 解析抓取结果
        raw_buff = response.data.decode('UTF-8')
        buff = raw_buff[raw_buff.find('{') :raw_buff.rfind('}')+1]
        result = json.loads(buff)

        # 取出数据
        if(result is None):
            print('reports is None = ',code)
            continue
        if('result' in result and result['result'] is not None):

            if('data' in result['result'] and result['result']['data'] is not None):
                reports = result['result']['data']
            else:
                print('result or data not in reports = ',code,'\n',result)
                continue
        else:
            print('result or data not in reports = ',code,'\n',result)
            continue


        # 更新数据库的请求列表
        update_requests = []
        # 循环处理所有报告数据
        for report in reports:
            if (report['REPORTDATE'] is None or len(report['REPORTDATE']) < 10):
                print('REPORTDATE ERROR  ', report)
                continue
            if (report['UPDATE_DATE'] is None or len(report['UPDATE_DATE']) < 10):
                print('UPDATE_DATE ERROR  ', report)
                continue
            doc = {
                'code': code,
                # REPORTDATE报告期
                'report_date': report['REPORTDATE'][:10],
                # 公告日期 # UPDATE_DATE最新公告时间
                'announced_date': report['UPDATE_DATE'][:10],
                # 每股收益（元）
                'eps': report['BASIC_EPS'],
                #每股收益（扣除）（元）
                'DEDUCT_BASIC_EPS':report['DEDUCT_BASIC_EPS'],
                #营业收入
                'TOTAL_OPERATE_INCOME':report['TOTAL_OPERATE_INCOME'],
                #净利润
                'PARENT_NETPROFIT':report['PARENT_NETPROFIT'],
                # YSTZ营业收入同比增长（%）
                'income_ratio':report['YSTZ'],
                # SJLTZ净利润同比增长（%）
                'netprofit_ratio':report['SJLTZ'],
                # BPS每股净资产(元)
                'BPS':report['BPS'],
                # MGJYXJJE每股经营现金流量(元)
                'operating_per_share':report['MGJYXJJE'],
                # YSHZ营业收入季度环比增长(%)
                'income_quart_ratio':report['YSHZ'],
                # SJLHZ 净利润季度环比增长(%)
                'netprofit_quart_ratio':report['SJLHZ'],
                # PUBLISHNAME 怀疑是行业分类
                'publish_name':report['PUBLISHNAME'],
                # NOTICE_DATE 首次公告日期
                'notice_date':report['NOTICE_DATE'],
                # QDATE 季度 2017Q3
                'quart_date':report['QDATE'],
                # SECURITY_CODE 股票代码1 600000SH
                'code1':report['SECUCODE'],
                # SECURITY_NAME_ABBR 名称
                'name':report['SECURITY_NAME_ABBR'],
                # TRADE_MARKET 交易所板块
                'trade_market':report['TRADE_MARKET'],
                # SECURITY_TYPE 股票类别 A股
                'security_type':report['SECURITY_TYPE'],
                #ASSIGNDSCRPT 利润分配 如"10派1.80元(含税)"
                'dividend':report['ASSIGNDSCRPT']
            }

            # 将更新请求添加到列表中，更新时的查询条件为code、report_date，为了快速保存数据，需要增加索引
            # db.finance_report.createIndex({'code':1, 'report_date':1})
            update_requests.append(
                UpdateOne(
                    {'code': code, 'report_date': doc['report_date']},
                    # upsert=True保证了如果查不到数据，则插入一条新数据
                    {'$set': doc}, upsert=True))

        # 如果更新数据的请求列表不为空，则写入数据库
        if len(update_requests) > 0:
            # 采用批量写入的方式，加快保存速度
            update_result = DB_CONN['finance_report'].bulk_write(update_requests, ordered=False)
            print('股票 %s, 财报，更新 %d, 插入 %d' %
                  (code, update_result.modified_count, update_result.upserted_count))


if __name__ == "__main__":
    crawl_finance_report()
