# -*- coding: utf-8 -*-
# @Time     : 2020/7/3 20:33
# @Author   ：Xie Huiqin
# @File     : pre_part.py
# @Software : orient_lab/jupyter notebook



import pandas as pd
import numpy as np
import datetime
from market_timing_lab import MeanReversion
from algoqi.data import D
D.load()

from backtest_class import backtest

class interval:
    """
    Some idea from 缠中说禅.

    Examples
    ---------
    import numpy as np
    import pandas as pd
    from market_timing_lab import MeanReversion
    from algoqi.data import D
    from pre_part import *
    D.load()
    #IC2006.CF，1minK分钟数据
    data=D.query_tsdata(datasource='future_kline_1min', symbols=['IC2006.CF'], fields=['open','high','low','close'], 
                        start='20200518', end='20200519', delivery_mode=D.DataDeliveryMode.DIRECT)
    data=data.reset_index()
    prices=data.rename(columns={'Symbol':'code','index':'DATETIME'})


    """


    @staticmethod
    def pre_part(part_last_df,date_col='DATETIME'):
        '''
    Target：
    -----------
    利用小周期K线（如1minK线）形态特征去预判是否会出现大周期K线（如5minK线）是否会出现顶/底分型。
    
    Examples:
    ------------

    ts_init=prices['DATETIME'][0]
    prices_contained_last = prices.loc[prices['DATETIME'] == ts_init, :].copy()
    prices_contained_last['k_num'] = prices_contained_last.index
    prices_contained_last['con_sig'] = 1
    part_last = prices_contained_last.copy()
    part_last['parting'] = 0
    part_last['pen_point'] = 0
    prices_later = prices.loc[prices['DATETIME'] > ts_init, :]
    for i in prices_later['DATETIME'].to_list():
        prices_latest = prices.loc[prices['DATETIME']==i, :]
        prices_contained_last = MeanReversion.contain_treat_latest(prices_contained_last, prices_latest)
        part_last = MeanReversion.part_old_latest(part_last, prices_contained_last)
        i_cur = i.strftime('%Y-%m-%d %H:%M:%S')
        if i_cur[-4:] == '0:00' or i_cur[-4:] == '5:00':   
            pre_part_df = interval.pre_part(part_last)
            print(pre_part_df)

    '''
        prices_cp = part_last_df.sort_values(by=[date_col])
        prices_cp.dropna(subset=['high', 'low'], inplace=True)
        prices_cp.reset_index(drop=True, inplace=True)
        prices_cp['pre_part'] = 0
    #     for date in prices_cp['DATETIME'].loc[-5:]:
    #         if date.minute % 5 == 0 :
        pre_max = pre_min = 0
        if len(part_last_df) >= 10:
            date_last_max = max(part_last_df.iloc[-10:-5]['high'])
            date_now_max = max(part_last_df.iloc[-5:]['high'])
            date_last_min = min(part_last_df.iloc[-10:-5]['low'])
            date_now_min = min(part_last_df.iloc[-5:]['low'])

            if date_now_max > date_last_max :
                if any(part_last_df.iloc[-6:-1]['parting'] == 1):                           
                    pre_max = 1
                elif any(part_last_df.iloc[-6:-1]['parting'] == 2): 
                    pre_max = 2
            if date_now_min < date_last_min :
                if any(part_last_df.iloc[-6:-1]['parting'] == -1):  
                    pre_min = -1  
                elif any(part_last_df.iloc[-6:-1]['parting'] == -2):  
                    pre_min = -2
        if pre_max > abs(pre_min):
            return pre_max
        elif pre_max < abs(pre_min):
            return pre_min
        else:
            return 0

#             if date_now_max > date_last_max and any(part_last_df.iloc[-6:-1]['parting']) > 0:                           
#                 #parting 可调整到2
# #                 prices_cp.iloc[-1]['pre_part'] = 1
#                 return 1
#             if date_now_min < date_last_min and any(part_last_df.iloc[-6:-1]['parting']) < 0:    
#                 #parting 可调整到2
# #                 prices_cp.iloc[-1]['pre_part'] = -1
#                 return -1
#         return 0
    #     date_last_1 = date - datetime.timedelta(minutes=5)
    #     date_last_5 = date - datetime.timedelta(minutes=1)
    #     date_now_1 = date
    #     date_now_5 = date + datetime.timedelta(minutes=4)
    #     date_last_max = max(prices_cp[(prices_cp['DATETIME'] >= date_last_1.strftime('%Y-%m-%d %H:%M:%S'))\
    #       &(prices_cp['DATETIME'] <=  date_last_5.strftime('%Y-%m-%d %H:%M:%S'))]['high'])
    #     date_now_max = max(prices_cp[(prices_cp['DATETIME'] >= date_now_1.strftime('%Y-%m-%d %H:%M:%S'))\
    #       &(prices_cp['DATETIME'] <=  date_now_5.strftime('%Y-%m-%d %H:%M:%S'))]['high'])
    #     prices_con = MeanReversion.contain_treat_latest(prices_contained_last, prices_latest)
    #     part_last_df.iloc[]
    #     if date_now_max > date_last_max:

    
    @staticmethod
    def pre_part1(part_last_df,date_col='DATETIME'):
        '''
    Target：
    -----------
    利用小周期K线（如1minK线）形态特征去预判是否会出现大周期K线（如5minK线）是否会出现顶/底分型。
    
    Examples:
    ------------

    ts_init=prices['DATETIME'][0]
    prices_contained_last = prices.loc[prices['DATETIME'] == ts_init, :].copy()
    prices_contained_last['k_num'] = prices_contained_last.index
    prices_contained_last['con_sig'] = 1
    part_last = prices_contained_last.copy()
    part_last['parting'] = 0
    part_last['pen_point'] = 0
    prices_later = prices.loc[prices['DATETIME'] > ts_init, :]
    for i in prices_later['DATETIME'].to_list():
        prices_latest = prices.loc[prices['DATETIME']==i, :]
        prices_contained_last = MeanReversion.contain_treat_latest(prices_contained_last, prices_latest)
        part_last = MeanReversion.part_old_latest(part_last, prices_contained_last)
        i_cur = i.strftime('%Y-%m-%d %H:%M:%S')
        if i_cur[-4:] == '0:00' or i_cur[-4:] == '5:00':   
            pre_part_df = interval.pre_part(part_last)
            print(pre_part_df)

    '''
        prices_cp = part_last_df.sort_values(by=[date_col])
        prices_cp.dropna(subset=['high', 'low'], inplace=True)
        prices_cp.reset_index(drop=True, inplace=True)
        prices_cp['pre_part'] = 0
    #     for date in prices_cp['DATETIME'].loc[-5:]:
    #         if date.minute % 5 == 0 :
        pre_max = pre_min = 0
        if len(part_last_df) >= 10:
            date_last_max = max(part_last_df.iloc[-10:-5]['high'])
            date_now_max = max(part_last_df.iloc[-5:]['high'])
            date_last_min = min(part_last_df.iloc[-10:-5]['low'])
            date_now_min = min(part_last_df.iloc[-5:]['low'])
            if date_now_max > date_last_max :
                pre_max = 1

            if date_now_min < date_last_min :
                pre_min = -1  


        if pre_max > abs(pre_min):
            return pre_max
        elif pre_max < abs(pre_min):
            return pre_min
        else:
            return 0

    @staticmethod
    def judge_2K(part_last_df,date_col='DATETIME'):
        '''
    Target:
    -----------
    判断大周期（如5minK线）合并处理之后，连续两根K线是上涨趋势还是下跌趋势。
    
    Examples:
    ------------

    ts_init=prices['DATETIME'][0]
    prices_contained_last = prices.loc[prices['DATETIME'] == ts_init, :].copy()
    prices_contained_last['k_num'] = prices_contained_last.index
    prices_contained_last['con_sig'] = 1
    part_last = prices_contained_last.copy()
    part_last['parting'] = 0
    part_last['pen_point'] = 0
    prices_later = prices.loc[prices['DATETIME'] > ts_init, :]
    for i in prices_later['DATETIME'].to_list():
        prices_latest = prices.loc[prices['DATETIME']==i, :]
        prices_contained_last = MeanReversion.contain_treat_latest(prices_contained_last, prices_latest)
        part_last = MeanReversion.part_old_latest(part_last, prices_contained_last)
        i_cur = i.strftime('%Y-%m-%d %H:%M:%S')
        if i_cur[-4:] == '0:00' or i_cur[-4:] == '5:00':   
            pre_part_df = interval.pre_part(part_last)
            print(pre_part_df)
    '''  
    
#     @staticmethod
#     def K_cut_update(prices,N,date_col='DATETIME'):
#             '''
#         Target:
#         -----------
#         将1min的数据迭代切割，计算顶底。
#         N = 5 #5minK一个K线包含5个1minK的单位K线。

#         Returns
#         -------
#         part_last_summary中‘parting’和‘pen_point’为迭代N次之后累计的均值

#         Examples:
#         ------------
#         N = 5
#         part_last_summary = interval.K_cut_update(prices,N,date_col='DATETIME')

#         '''   
#         #若N = 5，则每隔5min计算一次high low，DATETIME为该5min周期开始的第一分钟，生成prices_row_compute
#         prices_row_compute = prices[['DATETIME','code','high','low']].iloc[:-N+1].copy()
#         prices_row_compute['label'] = 0
#         label = 1
#         for i in prices['DATETIME'].to_list()[:-N+1]:
#             prices_row_compute.loc[prices_row_compute['DATETIME'] == i,'high']  = \
#             max(prices[prices['DATETIME'] >= i].iloc[:5]['high'])
#             prices_row_compute.loc[prices_row_compute['DATETIME'] == i,'low']  = \
#             min(prices[prices['DATETIME'] >= i].iloc[:5]['low']) 
#             if label > N:
#                 label = 1
#             prices_row_compute.loc[prices_row_compute['DATETIME'] == i,'label'] =label
#             label+=1

#         prices_row_dict = {}
#         for label_i in range(N):
#             ts_init=prices_row_compute['DATETIME'][label_i]
#             prices_contained_last = prices_row_compute.loc[prices_row_compute['DATETIME'] == ts_init, :].copy()
#             prices_contained_last['k_num'] = prices_contained_last.index
#             prices_contained_last['con_sig'] = 1
#             part_last = prices_contained_last.copy()
#             part_last['parting'] = 0
#             part_last['pen_point'] = 0
#             prices_row_dict[label_i+1] = {'prices_contained_last':prices_contained_last,'part_last':part_last}

#         for j in prices_row_compute['DATETIME'].to_list()[N:]:
#             prices_latest = prices_row_compute.loc[prices_row_compute['DATETIME']==j, :]
#             label_num = prices_row_compute.loc[prices_row_compute['DATETIME']==j, 'label'].iloc[0]
#             prices_contained_last = prices_row_dict[label_num]['prices_contained_last']
#             part_last = prices_row_dict[label_num]['part_last']
#             prices_contained_last = MeanReversion.contain_treat_latest(prices_contained_last, prices_latest)
#             part_last = MeanReversion.part_old_latest(part_last, prices_contained_last)
#             prices_row_dict[label_num]['prices_contained_last'] = prices_contained_last
#             prices_row_dict[label_num]['part_last'] = part_last

#         part_last_row = prices_row_dict[1]['part_last']
#         for label_j in range(2,N+1):
#             part_last_row = pd.concat([part_last_row,prices_row_dict[label_j]['part_last']])
#         part_last_row.sort_values(by=['DATETIME'],inplace = True)
#         part_last_row.reset_index(inplace = True,drop = True)
#         return part_last_row
        
    @staticmethod
    def K_cut(prices,N,date_col='DATETIME'):
        
        '''
        ###暂时启弃用###
        Target:
        -----------
        将1min的数据迭代切割，计算顶底。
        N = 5 #5minK一个K线包含5个1minK的单位K线。

        Returns
        -------
        part_last_summary中‘parting’和‘pen_point’为迭代N次之后累计的均值

        Examples:
        ------------
        N = 5
        part_last_summary = interval.K_cut(prices,N,date_col='DATETIME')

        '''    
        part_last_summary = prices.copy()
        part_last_summary['parting'] = 0
        part_last_summary['pen_point'] = 0
        for i in range(N):
            ts_init = prices['DATETIME'][i]

            prices_raw = prices.iloc[i:,:].copy()

            prices_contained_last = prices_raw.loc[prices_raw['DATETIME'] == ts_init, :].copy()
            prices_contained_last['k_num'] = prices_contained_last.index
            prices_contained_last['con_sig'] = 1

            part_last = prices_contained_last.copy()
            part_last['parting'] = 0
            part_last['pen_point'] = 0
            print('第{}/{}次迭代'.format(i+1,N))
            prices_later = prices_raw.loc[prices_raw['DATETIME'] > ts_init, :]
        #     print('list\n',prices_later['DATETIME'].to_list())
            last_time = 'init_time'
            for j in prices_later['DATETIME'].to_list():
        #         print('***j***',j)
                prices_latest = prices_raw.loc[prices_raw['DATETIME']==j, :]
                prices_contained_last = MeanReversion.contain_treat_latest(prices_contained_last, prices_latest)
                part_last_summary,part_last,last_time = interval.part_old_latest_interval\
                (part_last_summary,part_last, last_time,prices_contained_last)
        part_last_summary['parting'] = part_last_summary['parting'].apply(lambda x: x/N)
        part_last_summary['pen_point'] = part_last_summary['pen_point'].apply(lambda x: x/N)
        return part_last_summary

    @staticmethod 
    def part_old_latest_interval(part_last_summary,part_last, last_time,prices_contained_latest, date_col='DATETIME'):
        """
        ###暂时启弃用###
        被K_cut调用
        Parameters
        ----------
        part_last_summary : pd.DataFrame
            迭代找顶底笔的汇总df
        part_last : pd.DataFrame
            Last part result of last K line.
        prices_contained_latest : pd.DataFrame
            Latest contained prices we can get.
        date_col : str

        Returns
        -------

        Examples
        -------


        """
        part_last = part_last.sort_values(by=[date_col])
        part_last.reset_index(drop=True, inplace=True)
        prices_latest = prices_contained_latest.iloc[-1:, :].copy()
        part_last_index = part_last.index[-1]

        if prices_latest.index[0] == part_last_index:
            part_last.drop(index=part_last_index, inplace=True)
            part_last_index = part_last_index - 1

        prices_latest['parting'] = 0
        prices_latest['pen_point'] = 0
        part_last = pd.concat([part_last, prices_latest])

        if len(part_last[part_last['pen_point'] != 0]):
            last_parting_info = part_last[part_last['pen_point'] != 0].iloc[-1]
            last_parting = {'index': last_parting_info.name,  # k线合并后的ID
                            'k_num': last_parting_info['k_num'],  # k 线的ID
                            'parting': last_parting_info['parting'],  # 分型类型
                            'price': last_parting_info['high' if last_parting_info['parting'] > 0 else 'low']
                            # 前分型的最高价（顶分型）或最低价（底分型）
                            }
        else:
            last_parting = {'index': 0,  # k线合并后的ID
                            'k_num': part_last.loc[0, 'k_num'],  # k 线的ID
                            'parting': 0,  # 分型类型
                            'price': None  # 前分型的最高价（顶分型）或最低价（底分型）
                            }

        # part_last = pd.concat([part_last, prices_latest])
        if len(part_last) <= 2:
            part_last.reset_index(drop=True, inplace=True)
#             print('1***\n',part_last.head(10))
            if len(part_last) == 2:
                
                # part_last_summary.loc[part_last_summary['DATETIME'] == part_last.iloc[-1]['DATETIME'],'parting'] +=\
                #                             part_last.iloc[-1]['parting']
                part_last_summary.loc[part_last_summary['DATETIME'] == part_last.iloc[-2]['DATETIME'],'parting'] +=\
                                            part_last.iloc[-2]['parting']
                # part_last_summary.loc[part_last_summary['DATETIME'] == part_last.iloc[-1]['DATETIME'],'pen_point'] +=\
                #                             part_last.iloc[-1]['pen_point']
                part_last_summary.loc[part_last_summary['DATETIME'] == part_last.iloc[-2]['DATETIME'],'pen_point'] +=\
                                            part_last.iloc[-2]['pen_point']
                last_time = part_last.iloc[-2]['DATETIME']
            # elif len(part_last) == 1:
            #     part_last_summary.loc[part_last_summary['DATETIME'] == part_last.iloc[-1]['DATETIME'],'parting'] +=\
            #                                 part_last.iloc[-1]['parting']
            #     part_last_summary.loc[part_last_summary['DATETIME'] == part_last.iloc[-1]['DATETIME'],'pen_point'] +=\
            #                                 part_last.iloc[-1]['pen_point']
            else:
                pass
                
            # print('3***\n',part_last_summary.head(10))
            
            return part_last_summary,part_last,last_time

        if part_last.loc[part_last_index, 'high'] == max(part_last.loc[part_last_index - 1:part_last_index + 1, 'high']):
            if part_last.loc[part_last_index + 1, 'low'] < part_last.loc[part_last_index - 1, 'low'] and \
                    (part_last.loc[part_last_index + 1, 'high'] < (
                            part_last.loc[part_last_index - 1, 'high'] + part_last.loc[part_last_index - 1, 'low']) / 2):
                part_last.loc[part_last_index, 'parting'] = 2
            else:
                part_last.loc[part_last_index, 'parting'] = 1

            if (last_parting['parting'] < 0 and (part_last_index > last_parting['index'] + 3)) \
                    or last_parting['parting'] == 0:
                part_last.loc[part_last_index, 'pen_point'] = 1
                # last_parting['index'], last_parting['k_num'], last_parting['parting'], last_parting['price'] = \
                #     part_last_index, part_last.loc[part_last_index, 'k_num'], 1, part_last.loc[part_last_index, 'high']
            if last_parting['parting'] > 0 and last_parting['price'] < part_last.loc[part_last_index, 'high']:
                part_last.loc[part_last_index, 'pen_point'] = 1
                
                part_last_summary.loc[part_last_summary['DATETIME'] == \
                                        part_last.iloc[last_parting['index']]['DATETIME'],'pen_point'] -=\
                                        part_last.iloc[last_parting['index']]['pen_point']
                part_last.loc[last_parting['index'], 'pen_point'] = 0
                # last_parting['index'], last_parting['k_num'], last_parting['parting'], last_parting['price'] = \
                #     part_last_index, part_last.loc[part_last_index, 'k_num'], 1, part_last.loc[part_last_index, 'high']

        if part_last.loc[part_last_index, 'low'] == min(part_last.loc[part_last_index - 1:part_last_index + 1, 'low']):
            # and all(prices_cp.loc[i - 2:i - 1, 'parting'] == 0):
            if part_last.loc[part_last_index + 1, 'high'] > part_last.loc[part_last_index - 1, 'high'] and \
                    (part_last.loc[part_last_index + 1, 'low'] > (
                            part_last.loc[part_last_index - 1, 'high'] + part_last.loc[part_last_index - 1, 'low']) / 2):
                part_last.loc[part_last_index, 'parting'] = -2
            else:
                part_last.loc[part_last_index, 'parting'] = -1

            # judge the pen_point
            if (last_parting['parting'] > 0 and (part_last_index > last_parting['index'] + 3)) \
                    or last_parting['parting'] == 0:
                part_last.loc[part_last_index, 'pen_point'] = -1
                # last_parting['index'], last_parting['k_num'], last_parting['parting'], last_parting['price'] = \
                #     part_last_index, part_last.loc[part_last_index, 'k_num'], -1, part_last.loc[part_last_index, 'low']
            if last_parting['parting'] < 0 and last_parting['price'] > part_last.loc[part_last_index, 'low']:
                part_last.loc[part_last_index, 'pen_point'] = -1
                part_last_summary.loc[part_last_summary['DATETIME'] == \
                                        part_last.iloc[last_parting['index']]['DATETIME'],'pen_point'] -=\
                                        part_last.iloc[last_parting['index']]['pen_point']
                part_last.loc[last_parting['index'], 'pen_point'] = 0
                # last_parting['index'], last_parting['k_num'], last_parting['parting'], last_parting['price'] = \
                #     part_last_index, part_last.loc[part_last_index, 'k_num'], -1, part_last.loc[part_last_index, 'low']



        # print('****part_last_parting\n',part_last.iloc[-2]['parting'])
#         part_last_summary.loc[part_last_summary['DATETIME'] == part_last.iloc[-1]['DATETIME'],'parting'] +=\
#                                     part_last.iloc[-1]['parting']
        if part_last.iloc[-2]['DATETIME'] != last_time:
            part_last_summary.loc[part_last_summary['DATETIME'] == part_last.iloc[-2]['DATETIME'],'parting'] +=\
                                        part_last.iloc[-2]['parting']
    #         part_last_summary.loc[part_last_summary['DATETIME'] == part_last.iloc[-1]['DATETIME'],'pen_point'] +=\
    #                                     part_last.iloc[-1]['pen_point']
            part_last_summary.loc[part_last_summary['DATETIME'] == part_last.iloc[-2]['DATETIME'],'pen_point'] +=\
                                        part_last.iloc[-2]['pen_point']
            # print('***part_last_summary\n',part_last_summary.head(10))
#         if str(part_last.iloc[-2]['DATETIME']) == '2020-05-18 09:35:00':
#             print('\n****time',part_last.iloc[-2]['DATETIME'])
#             print('\n1111****part_last\n',part_last)
#             print('\n1111****part_last_parting',part_last.iloc[-2]['parting'])
#             print('\n1111***part_last_summary\n',part_last_summary.head(10))
        last_time = part_last.iloc[-2]['DATETIME']

        return part_last_summary,part_last,last_time
        
    @staticmethod    
    def K_cut_init(prices,N,date_col='DATETIME'):
        #若N = 5，则每隔5min计算一次high low，DATETIME为该5min周期开始的第一分钟，生成prices_row_compute
        prices_row_compute = prices[['DATETIME','code','high','low']].iloc[N-1:].copy()
        prices_row_compute['label'] = 0
        label = N
        for i in prices['DATETIME'].to_list()[N-1:]:
            prices_row_compute.loc[prices_row_compute['DATETIME'] == i,'high']  = \
            max(prices[prices['DATETIME'] <= i].iloc[-N:]['high'])
            prices_row_compute.loc[prices_row_compute['DATETIME'] == i,'low']  = \
            min(prices[prices['DATETIME'] <= i].iloc[-N:]['low']) 
            if label > N:
                label = 1
            prices_row_compute.loc[prices_row_compute['DATETIME'] == i,'label'] =label
            label+=1

        prices_row_dict = {}
        prices_row_dict_shift = {}
        for label_i in range(N):
            ts_init=prices_row_compute['DATETIME'].iloc[label_i]
            prices_contained_last = prices_row_compute.loc[prices_row_compute['DATETIME'] == ts_init, :].copy()
            prices_contained_last['k_num'] = prices_contained_last.index
            prices_contained_last['con_sig'] = 1
            part_last = prices_contained_last.copy()
            part_last['parting'] = 0
            part_last['pen_point'] = 0
            label_num =  prices_row_compute.loc[prices_row_compute['DATETIME']==ts_init, 'label'].iloc[0]
            prices_row_dict[label_num] = {'prices_contained_last':prices_contained_last,'part_last':part_last}
            prices_row_dict_shift[label_num] = part_last
        return prices_row_compute,prices_row_dict,prices_row_dict_shift
#         #若N = 5，则每隔5min计算一次high low，DATETIME为该5min周期开始的第一分钟，生成prices_row_compute
#         prices_row_compute = prices[['DATETIME','code','high','low']].iloc[N:].copy()
#         prices_row_compute['label'] = 0
#         label = 1
#         for i in prices['DATETIME'].to_list()[N:]:
#             prices_row_compute.loc[prices_row_compute['DATETIME'] == i,'high']  = \
#             max(prices[prices['DATETIME'] <= i].iloc[-N:]['high'])
#             prices_row_compute.loc[prices_row_compute['DATETIME'] == i,'low']  = \
#             min(prices[prices['DATETIME'] <= i].iloc[-N:]['low']) 
#             if label > N:
#                 label = 1
#             prices_row_compute.loc[prices_row_compute['DATETIME'] == i,'label'] =label
#             label+=1

#         prices_row_dict = {}
#         prices_row_dict_shift = {}
#         for label_i in range(N):
#             ts_init=prices_row_compute['DATETIME'].iloc[label_i]
#             prices_contained_last = prices_row_compute.loc[prices_row_compute['DATETIME'] == ts_init, :].copy()
#             prices_contained_last['k_num'] = prices_contained_last.index
#             prices_contained_last['con_sig'] = 1
#             part_last = prices_contained_last.copy()
#             part_last['parting'] = 0
#             part_last['pen_point'] = 0
#             prices_row_dict[label_i+1] = {'prices_contained_last':prices_contained_last,'part_last':part_last}
#             prices_row_dict_shift[label_i+1] = part_last
#         return prices_row_compute,prices_row_dict,prices_row_dict_shift


    @staticmethod    
    def K_cut_update(N,date,prices_row_compute,prices_row_dict,prices_row_dict_shift):
        '''
        Target:
        -----------
        若N = 5 #5minK一个K线包含5个1minK的单位K线。
        将1min的数据迭代切割，计算5minK的顶底，再按新信号进行买卖


        Returns
        -------
        part_last_summary中‘parting’和‘pen_point’为迭代N次之后累计的均值

        Examples:
        ------------
        N = 5
        prices_row_compute,prices_row_dict,prices_row_dict_shift = K_cut_init(prices,N,date_col='DATETIME')
        for date in prices_row_compute['DATETIME'].to_list()[N:]:
            prices_row_dict,part_last_row,prices_row_dict_shift = K_cut_update\
            (N,date,prices_row_compute,prices_row_dict,prices_row_dict_shift)
        ''' 

        prices_latest = prices_row_compute.loc[prices_row_compute['DATETIME']==date, :]
        label_num = prices_row_compute.loc[prices_row_compute['DATETIME']==date, 'label'].iloc[0]
        prices_contained_last = prices_row_dict[label_num]['prices_contained_last']
        part_last = prices_row_dict[label_num]['part_last']
        prices_contained_last = MeanReversion.contain_treat_latest(prices_contained_last, prices_latest)
        part_last = MeanReversion.part_old_latest(part_last, prices_contained_last)
        prices_row_dict[label_num]['prices_contained_last'] = prices_contained_last
        prices_row_dict[label_num]['part_last'] = part_last

        #part_last_row_shift : 将顶底笔标记在最后一根K线，而不是第二根
        part_last_shift = part_last.copy()
        part_last_shift['parting'] = part_last_shift['parting'].shift(1)
        part_last_shift['pen_point'] = part_last_shift['pen_point'].shift(1)
        part_last_shift['high'] = part_last_shift['high'].shift(1)
        part_last_shift['low'] = part_last_shift['low'].shift(1)
        part_last_shift.fillna({'parting':0,'pen_point':0},inplace = True)
        prices_row_dict_shift[label_num] = part_last_shift


        part_last_row = prices_row_dict_shift[1].copy()
        for label_j in range(2,N+1):
            part_last_row = pd.concat([part_last_row,prices_row_dict_shift[label_j]])
        part_last_row.sort_values(by=['DATETIME'],inplace = True)
        part_last_row.reset_index(inplace = True,drop = True)

        return prices_row_dict,part_last_row,prices_row_dict_shift
    
    @staticmethod    
    def K_cut_init1(prices,N,date_col='DATETIME'):
        #若N = 5，则每隔5min计算一次high low，DATETIME为该5min周期开始的第一分钟，生成prices_row_compute
        prices_row_compute = prices[['DATETIME','code','high','low']].iloc[N-1:].copy()
        prices_row_compute['label'] = 0
        label = 5
        for i in prices['DATETIME'].to_list()[N-1:]:
            prices_row_compute.loc[prices_row_compute['DATETIME'] == i,'high']  = \
            max(prices[prices['DATETIME'] <= i].iloc[-N:]['high'])
            prices_row_compute.loc[prices_row_compute['DATETIME'] == i,'low']  = \
            min(prices[prices['DATETIME'] <= i].iloc[-N:]['low']) 
            if label > N:
                label = 1
            prices_row_compute.loc[prices_row_compute['DATETIME'] == i,'label'] =label
            label+=1

        prices_row_dict = {}
        for label_i in range(N):
            ts_init=prices_row_compute['DATETIME'].iloc[label_i]
            prices_contained_last = prices_row_compute.loc[prices_row_compute['DATETIME'] == ts_init, :].copy()
            prices_contained_last['k_num'] = prices_contained_last.index
            prices_contained_last['con_sig'] = 1
            part_last = prices_contained_last.copy()
            part_last['parting'] = 0
            part_last['pen_point'] = 0
            label_num =  prices_row_compute.loc[prices_row_compute['DATETIME']==ts_init, 'label'].iloc[0]
            prices_row_dict[label_num] = {'prices_contained_last':prices_contained_last,'part_last':part_last}
        return prices_row_compute,prices_row_dict
    
    
    @staticmethod    
    def K_cut_update1(N,date,prices_row_compute,prices_row_dict):
        '''
        Target:
        -----------
        若N = 5 #5minK一个K线包含5个1minK的单位K线。
        将1min的数据迭代切割，计算5minK的顶底，再按新信号进行买卖
        用于s0706_00_7

        Returns
        -------
        part_last_summary中‘parting’和‘pen_point’为迭代N次之后累计的均值

        Examples:
        --------
        N = 5
        prices_row_compute,prices_row_dict = interval.K_cut_init1(prices,N,date_col='DATETIME')
        for date in prices_row_compute['DATETIME'].to_list()[N:]:
            prices_row_dict = interval.K_cut_update1(N,date,prices_row_compute,prices_row_dict)
        ''' 

        prices_latest = prices_row_compute.loc[prices_row_compute['DATETIME']==date, :]
        label_num = prices_row_compute.loc[prices_row_compute['DATETIME']==date, 'label'].iloc[0]
        prices_contained_last = prices_row_dict[label_num]['prices_contained_last']
        part_last = prices_row_dict[label_num]['part_last']
        prices_contained_last = MeanReversion.contain_treat_latest(prices_contained_last, prices_latest)
        part_last = MeanReversion.part_old_latest(part_last, prices_contained_last)
        prices_row_dict[label_num]['prices_contained_last'] = prices_contained_last
        prices_row_dict[label_num]['part_last'] = part_last

        return prices_row_dict
    
    @staticmethod 
    def interval_func_init(prices,N):
        '''
          被interval_func调用
        '''
    
        #  使用1minK，将连续5根K线合并成5minK线，两根合成5minK线，与之后的1根1minK、合成2minK线（连续2根1minK）、合成3minK（连续3根1minK）、...、合成5minK（连续5根1minK）
        #，作为输入，计算parting和pen_point，下一个1minK与之前的两个合成5minK做输入，以此类推。
        prices_row_compute = prices[['DATETIME','code','high','low']].copy()
        prices_row_compute['label'] = 0
        label = 1
        for i in prices['DATETIME'].to_list():
            if label > N:
                label = 1
            prices_row_compute.loc[prices_row_compute['DATETIME'] == i,'label'] =label

            prices_row_compute.loc[prices_row_compute['DATETIME'] == i,'high']  = \
                max(prices[prices['DATETIME'] <= i].iloc[-label:]['high'])
            prices_row_compute.loc[prices_row_compute['DATETIME'] == i,'low']  = \
                min(prices[prices['DATETIME'] <= i].iloc[-label:]['low']) 


            label+=1


        prices_row_dict = {}
        ts_init = prices_row_compute['DATETIME'].iloc[0]
        prices_contained_last = prices_row_compute.loc[prices_row_compute['DATETIME'] == ts_init, :].copy()
        prices_contained_last['k_num'] = 1
        prices_contained_last['con_sig'] = 1
        part_last = prices_contained_last.copy()
        part_last['parting'] = 0
        part_last['pen_point'] = 0
        prices_row_dict = {'prices_contained_last':prices_contained_last,'part_last':part_last}
        return prices_row_compute,prices_row_dict

  
    def interval_func(N,date,prices_row_compute,prices_row_dict):
        '''
        Target:
        -----------
        若N = 5 #5minK一个K线包含5个1minK的单位K线。
        区间套策略

        Examples:
        ------------
        N = 5
        prices_row_compute,prices_row_dict = interval.interval_func_init(prices,N)
        for date in prices_row_compute['DATETIME'].to_list():
            prices_row_dict,part_last = interval.interval_func(N,date,prices_row_compute,prices_row_dict)
        ''' 
        prices_latest = prices_row_compute.loc[prices_row_compute['DATETIME']==date, :]

        label_num = prices_row_compute.loc[prices_row_compute['DATETIME']==date, 'label'].iloc[0]
        prices_contained_last = prices_row_dict['prices_contained_last']
        part_last = prices_row_dict['part_last']
        prices_contained_last = MeanReversion.contain_treat_latest(prices_contained_last, prices_latest)
        part_last = MeanReversion.part_old_latest(part_last, prices_contained_last)



        if  label_num == N:
            prices_row_dict['prices_contained_last'] = prices_contained_last
            prices_row_dict['part_last'] = part_last


        return prices_row_dict,part_last
    
    
class K_cut:
    @staticmethod    
    def aggre_tick(tick_data,m = 60,n = 60*5):

        '''
        Target:
        -----------
        注意：一次输入一天的tick_data
        时间切割的准备工作
        按照每m秒聚合一次，每次聚合过去n秒的tick数据，生成的表格，并且标注好label
        如实现每1min(60s)聚合一次，聚合窗口为5min(60*5)
        输入：聚合间隔m,聚合窗口n,单位秒

        Returns
        -------
        kcut_res_data按照每m秒聚合一次，每次聚合过去n秒的tick数据，所生成的表格。同一label的数据之间才可以做顶底等的计算。

        Examples:
        --------
        start_date = '20190923'
        tick_data_batch = D.query_tsdata(datasource='future_tick', symbols=['IC1910.CFE'],\
                                         fields='price',start=start_date, end=start_date, delivery_mode='batch_by_symbol')
        for d in tick_data_batch:
            tick_data = d
        tick_data = tick_data[start_date + ' 09:30:00':start_date + ' 14:00:00']
        
        kcut_res_data = K_cut.aggre_tick(tick_data = tick_data,m = 60,n = 60*5)
        ''' 
        
        def append_kline(tick_data,N,start_date,kcut_res_data,time = '11:30:00'):
        #增加遗漏的数据
            kcut_res_data.sort_index(inplace=True)
            label_data = kcut_res_data[:start_date + ' '+time]
#             label_data = label_data.dropna(subset = ['high','low'],how = 'all').copy()
            label_data.sort_index(inplace=True)
            label_latest = label_data['label'].iloc[-1]
            if label_latest +1 > N:
                label = 1
            else:
                label = label_latest + 1

            ts_later = pd.Timestamp(start_date + ' '+time)
            ts = ts_later - datetime.timedelta(seconds = n)

            aggre_piece = tick_data[ts:ts_later].iloc[:-1]
            ts_index = ts_later
            kcut_res_data.loc[ts_index,'high'] = aggre_piece['price'].max()
            kcut_res_data.loc[ts_index,'low'] = aggre_piece['price'].min()
            kcut_res_data.loc[ts_index,'open'] = aggre_piece['price'].iloc[0]
            kcut_res_data.loc[ts_index,'close'] = aggre_piece['price'].iloc[-1]
            kcut_res_data.loc[ts_index,'label'] = label
            
            #修改插入点之后的label ##未修改
            label_data_after =  kcut_res_data[start_date + ' '+time:].iloc[1:,:]
            if len(label_data_after) != 0:
                label_data_after['label'] = label_data_after['label'].apply(lambda x:x+1 if x < N else 1 )
            
            
            
            kcut_res_data.sort_index(inplace=True)
            return kcut_res_data
            
        # #可容忍aggre_piece最少数据行min_num
        if m <= 0 or n <=0:
            print('警告：聚合间隔m或聚合窗口n应该为大于0的整数。')
            return
        if m > n:
            print('警告：聚合间隔m应该小于聚合窗口n。')
            return
        N = n/m
        if (N - N//1) != 0:
            print('警告：N = n/m，N不是整数，无法进行时间切割。')
            return 

        tick_data.sort_index(inplace=True)
        tick_aggre_data = pd.DataFrame(columns = {'open','high','low','close','label'},index = tick_data.index)
        start_date = tick_data.index[0].strftime("%Y%m%d")
        ts = tick_data[start_date + ' 09:30:00'].index[0]
        label = 1
        
        while ts < pd.Timestamp(start_date + ' 15:00:00') - datetime.timedelta(seconds = n):
            ts_later = ts + datetime.timedelta(seconds = n) 

            if ts > pd.Timestamp(start_date + ' 11:30:00') - datetime.timedelta(seconds = n)\
                        and ts < pd.Timestamp(start_date + ' 11:30:00'):  

                ts_later = (datetime.timedelta(seconds = n) - (pd.Timestamp(start_date + ' 11:30:00') - ts))\
                                                            + pd.Timestamp(start_date + ' 13:00:00')


#             if ts.strftime('%H:%M:%S') == '13:00:00':
#                 handle_middle = True
#                 continue
                
            aggre_piece = tick_data[ts:ts_later].iloc[:-1]
            if len(aggre_piece) != 0:
    #             ts_index = aggre_piece.index[-1]
                #输出kcut_res_data，各行信息是对应时间戳之前的信息，不包含该时间戳的信息
                ts_index = ts_later
                tick_aggre_data.loc[ts_index,'high'] = aggre_piece['price'].max()
                tick_aggre_data.loc[ts_index,'low'] = aggre_piece['price'].min()
                tick_aggre_data.loc[ts_index,'open'] = aggre_piece['price'].iloc[0]
                tick_aggre_data.loc[ts_index,'close'] = aggre_piece['price'].iloc[-1]
                tick_aggre_data.loc[ts_index,'label'] = label
            label += 1
            if label > N:
                label = 1

            if ts < pd.Timestamp(start_date + ' 11:30:00') and \
                        ts > pd.Timestamp(start_date + ' 11:30:00') - datetime.timedelta(seconds = m):
                ts = (datetime.timedelta(seconds = m) - (pd.Timestamp(start_date + ' 11:30:00') - ts))\
                                    + pd.Timestamp(start_date + ' 13:00:00')
            else:
                ts = ts +  datetime.timedelta(seconds = m)
                


        
        #kcut_res_data 按所需聚合间隔,聚合窗口做出的
        kcut_res_data = tick_aggre_data.dropna(subset = ['high','low'],how = 'all').copy()
#         kcut_res_data.sort_index(inplace=True)
        
#         #加上缺少的最后一行 15:00:00   
#         label_latest = kcut_res_data['label'].iloc[-1]
#         if label_latest +1 > N:
#             label_end = 1
#         else:
#             label_end = label_latest + 1
        
        
#         ts_later = pd.Timestamp(start_date + ' 15:00:00')
#         ts = ts_later - datetime.timedelta(seconds = n)
#         aggre_piece = tick_data[ts:ts_later].iloc[:-1]
#         ts_index = ts_later
#         kcut_res_data.loc[ts_index,'high'] = aggre_piece['price'].max()
#         kcut_res_data.loc[ts_index,'low'] = aggre_piece['price'].min()
#         kcut_res_data.loc[ts_index,'open'] = aggre_piece['price'].iloc[0]
#         kcut_res_data.loc[ts_index,'close'] = aggre_piece['price'].iloc[-1]
#         kcut_res_data.loc[ts_index,'label'] = label_end
#         if handle_middle:
        kcut_res_data = append_kline(tick_data,N,start_date,kcut_res_data,time = '11:30:00')
        kcut_res_data = kcut_res_data.drop(index = kcut_res_data[start_date+' '+'13:00:00'].index)
        kcut_res_data = append_kline(tick_data,N,start_date,kcut_res_data,time = '15:00:00')
#         kcut_res_data[start_date+' 11:30:00':]['label'].iloc[1:] =\
#                                         kcut_res_data[start_date+' 11:30:00':]['label'].iloc[1:].apply(lambda x:x+1 if x < N else 1)
        
        
        kcut_res_data = kcut_res_data[['open','high','low','close','label']]

        
        return kcut_res_data  
    
    
    @staticmethod 
    def kline_merge_strategy(k_min = 30,start_date = '20200102',symbols=['IC2001.CFE']):
        '''
        用tick合成一天之内分钟级别的k线
        example:
        ---------
        k_min = 30 : tick合成30minK
        kcut_res_data = K_cut.kline_merge_strategy(k_min = 30,start_date = '20200102',symbols=['IC2001.CFE'])
        '''

        tick_data_batch = D.query_tsdata(datasource='future_tick', symbols=symbols,\
                                         fields='price',start=start_date, end=start_date, delivery_mode='batch_by_symbol')
        for d in tick_data_batch:
            tick_data = d

        tick_data = tick_data[start_date + ' 09:30:00':start_date + ' 15:00:00']
        kcut_res_data = K_cut.aggre_tick(tick_data = tick_data,m = 60*k_min,n = 60*k_min)
        #调整输出格式
        kcut_res_data=kcut_res_data.reset_index()
        kcut_res_data=kcut_res_data.rename(columns={'Symbol':'code','index':'DATETIME'})
        kcut_res_data['DATETIME'] = kcut_res_data['DATETIME'].apply(lambda x:pd.Timestamp(x.strftime('%Y-%m-%d %H:%M:%S')))
        kcut_res_data['code'] = symbols[0][:-1]
        kcut_res_data.drop('label',axis = 1,inplace = True)
        kcut_res_data.sort_values('DATETIME',inplace = True)
        #检查是否有重复行
        if any(kcut_res_data['DATETIME'].duplicated()):
            print('warning: kline_merge_strategy输出有重复时间戳')
            return
        else:
            pass
        return kcut_res_data
    
    @staticmethod
    def long_Kline_merge(start = '20190102',end = '20191231',k_min = 1):
        '''
        获取从start到end这段时间内，合成k_min分钟K线。
        '''
        # 获取交易日
        trading_day_data = D.query_ext_factor(datasource='wind_eod_index_price', symbols=['000001.SH'],\
                                              fields=['S_DQ_CLOSE'], start=start, end=end)
        trading_day_data.reset_index(inplace = True)
        trading_day_data.rename({'ts':'trading_day'},axis = 1,inplace= True)
        trading_day_data =trading_day_data['trading_day']
        trading_day_data = trading_day_data.apply(lambda x :x.strftime('%Y%m%d') )
        #获取 IC
        IC_data = backtest.get_IC_date(start = start,end = end)
        #使用class，并concat
        kline_df = pd.DataFrame()
        for start_date in trading_day_data:
            symbols = []
            symbols.append(IC_data[(IC_data['ENDDATE'] >= start_date) &
                               (IC_data['STARTDATE'] <= start_date)]['FS_MAPPING_WINDCODE'].iloc[0])
            try:
                kline= K_cut.kline_merge_strategy(k_min = k_min,start_date = start_date,symbols=symbols)
            except TypeError:
                pass
            else:
                kline_df = pd.concat([kline_df,kline]).reset_index(drop = True)

        return kline_df


    
    @staticmethod   
    def K_cut_init_tick(prices_row_compute ,N ):
        if N - N//1 != 0:
            print('警告：N应该为整数。')
            return
        prices_row_dict = {}
        for label_i in range(int(N)):
            ts_init=prices_row_compute['DATETIME'].iloc[label_i]
            prices_contained_last = prices_row_compute.loc[prices_row_compute['DATETIME'] == ts_init, :].copy()
            prices_contained_last['k_num'] = prices_contained_last.index
            prices_contained_last['con_sig'] = 1
            part_last = prices_contained_last.copy()
            part_last['parting'] = 0
            part_last['pen_point'] = 0
            label_num =  prices_row_compute.loc[prices_row_compute['DATETIME']==ts_init, 'label'].iloc[0]
            prices_row_dict[label_num] = {'prices_contained_last':prices_contained_last,'part_last':part_last}
        return prices_row_dict

    @staticmethod  
    def K_cut_update_tick(N,date,prices_row_compute,prices_row_dict):
        '''
        Target:
        -----------
        输出时间切割策略下的顶底笔

        Returns
        -------


        Examples:
        --------
        from interval_theory import K_cut 
        #n/m必须是非零整数，n必须大于m，n和m都必须大于0的整数
        m = 30
        n = 60*2
        N = int(n/m) 
        #kcut_res_data，各行信息是对应时间戳之前的信息，不包含该时间戳的信息
        kcut_res_data = K_cut.aggre_tick(tick_data = tick_data,m = m,n = n)

        # 修改数据输出格式，建议仔细观察
        kcut_res_data.reset_index(inplace = True)
        kcut_res_data.rename({'index':'DATETIME'} ,axis =1,inplace = True)
        kcut_res_data['DATETIME'] = kcut_res_data['DATETIME'].apply(lambda x:x.strftime('%Y-%m-%d %H:%M:%S'))
        kcut_res_data['DATETIME'] = kcut_res_data['DATETIME'].apply(lambda x:pd.Timestamp(x))

        prices_row_dict = K_cut.K_cut_init_tick(prices_row_compute = kcut_res_data,N = N)
        for date in kcut_res_data['DATETIME'].to_list()[N:]:
            prices_row_dict = K_cut.K_cut_update_tick(N,date,prices_row_compute = kcut_res_data,prices_row_dict = prices_row_dict)
        ''' 

        prices_latest = prices_row_compute.loc[prices_row_compute['DATETIME']==date, :]
        label_num = prices_row_compute.loc[prices_row_compute['DATETIME']==date, 'label'].iloc[0]
        prices_contained_last = prices_row_dict[label_num]['prices_contained_last']
        part_last = prices_row_dict[label_num]['part_last']
        prices_contained_last = MeanReversion.contain_treat_latest(prices_contained_last, prices_latest)
        part_last = MeanReversion.part_old_latest(part_last, prices_contained_last)
        prices_row_dict[label_num]['prices_contained_last'] = prices_contained_last
        prices_row_dict[label_num]['part_last'] = part_last

        return prices_row_dict

    