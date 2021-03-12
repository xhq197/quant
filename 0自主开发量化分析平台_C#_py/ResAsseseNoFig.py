# -*- coding: utf-8 -*-
# @Time     : 2020/07/24 
# @Author   ：Li Wenting
# @File     : ResultAssese.py
# @Software : 

import numpy as np
import pandas as pd


class ResultAssese:

    def RetPerSize(trades_df):
        '''
        Function:calculate the return per size
        Parameters:
        pos_df:DataFrame
        '''
        open_trades = trades_df[trades_df['open_close'] == 'OPEN']
        close_trades = trades_df[trades_df['open_close'] == 'CLOSE']
        open_trades.reset_index(inplace = True)
        close_trades.reset_index(inplace = True)
        ret_long = close_trades[close_trades['LS'] == 'LONG']['price'] \
                   - open_trades[open_trades['LS'] == 'LONG']['price']
        ret_long.index = open_trades[open_trades['LS'] == 'LONG']['ts']
        ret_short = open_trades[open_trades['LS'] == 'SHORT']['price'] \
                   - close_trades[close_trades['LS'] == 'SHORT']['price']
        ret_short.index = open_trades[open_trades['LS'] == 'SHORT']['ts']
        ret_all = pd.concat([ret_long,ret_short])
        ret_all = ret_all.sort_index()
        ret_per_size = pd.DataFrame({'ret_long':ret_long,
                                'ret_short':ret_short,
                                'ret_all':ret_all
                                })
        ret_per_size = ret_per_size.fillna(0)
        return ret_per_size

    def RetPerSize_update(trades_df):
        '''
        将return per size的时间戳放在平仓时间
        Function:calculate the return per size
        Parameters:
        pos_df:DataFrame
        '''
        open_trades = trades_df[trades_df['open_close'] == 'OPEN']
        close_trades = trades_df[trades_df['open_close'] == 'CLOSE']
        open_trades.reset_index(inplace = True)
        close_trades.reset_index(inplace = True)
        ret_long = close_trades[close_trades['LS'] == 'LONG']['price'] \
                   - open_trades[open_trades['LS'] == 'LONG']['price']
        ret_long.index = close_trades[close_trades['LS'] == 'LONG']['ts']
        ret_short = open_trades[open_trades['LS'] == 'SHORT']['price'] \
                   - close_trades[close_trades['LS'] == 'SHORT']['price']
        ret_short.index = close_trades[close_trades['LS'] == 'SHORT']['ts']
        ret_all = pd.concat([ret_long,ret_short])
        ret_all = ret_all.sort_index()
        ret_per_size = pd.DataFrame({'ret_long':ret_long,
                                'ret_short':ret_short,
                                'ret_all':ret_all
                                })
        ret_per_size = ret_per_size.fillna(0)
        return ret_per_size

    def ProfitCossRatio(ret_df):
        '''
        ProfitCrossRatio =  total profit / total coss
        统计多仓、空仓、多空仓位单笔收益为正的累计值/单笔收益为负的累计值
        Parameters:DataFrame
        return:
        '''
        total_profit = ret_df[ret_df>0].sum(axis = 0)
        total_coss = - ret_df[ret_df<0].sum(axis = 0)
        ProfitCossRatio = total_profit/total_coss
        return ProfitCossRatio
    
    def TradesCount(trades_df):
        '''
        统计交易次数,open long和close long算两次
        '''
        total = len(trades_df)
        long = len(trades_df[trades_df['LS'] == 'LONG'])
        short = len(trades_df[trades_df['LS'] == 'SHORT'])
        count = dict(tatol = total, long = long,short = short)
        return count
    
    def ProfitCount(ret_df):
        '''
        分别统计long、short盈利次数
        '''
        count_profit = ret_df[ret_df>0].count(axis = 0)
        count_coss =  ret_df[ret_df<0].count(axis = 0)
        count = pd.DataFrame({'count_profit':count_profit,'count_coss':count_coss})
        return count

    def ProfitRate(ret_df):
        '''
        ProfitRate = the times of profit / the times of coss
        Parameters:DataFrame
        return:
        '''
        count_profit = ret_df[ret_df>0].count(axis = 0)
        count_coss =  ret_df[ret_df<0].count(axis = 0)
        ProfitRate = count_profit/(count_coss+count_profit)
        return ProfitRate

    
    def  PosTime(trades_df):
        '''
        Calculate the position time
        Parameters:DataFrame
        return:
        '''
        trades_time = trades_df[['LS','open_close']]
        trades_time['datetime'] = trades_time.index.strftime("%Y-%m-%d %H:%M:%S")   #series，str
        trades_time.index = trades_time.index.strftime("%Y-%m-%d %H:%M:%S")
        trades_time.index = pd.to_datetime(trades_time.index)                       #timestamp
        close_time = trades_time[trades_time['open_close'] == 'CLOSE']
        open_time = trades_time[trades_time['open_close'] == 'OPEN']
        close_time['pos_time'] = close_time.index - open_time.index
        for i in range(0,len(open_time)):
            if open_time['datetime'][i][-8:]<'11:30:00' and close_time['datetime'][i][-8:]>'13:30:00':
                close_time['pos_time'][i] = close_time['pos_time'][i] - pd.to_timedelta(2,'h')
        pos_time = close_time.drop(labels = ['datetime' , 'open_close'],axis = 1)
        return pos_time

    def  MeanPosTime(pos_time):
        '''
        Calculate the mean of position time
        Parameters:DataFrame
        return:
        '''
        total = pd.Timedelta(np.mean(pos_time['pos_time'].values),'m')   #这里没有剔除中午的停盘时间
        long = pd.Timedelta(np.mean(pos_time[pos_time['LS'] == 'LONG']['pos_time'].values),'m')
        short = pd.Timedelta(np.mean(pos_time[pos_time['LS'] == 'SHORT']['pos_time'].values),'m')
        return {'total':total,'long':long,'short':short}
    
    def res_assess(trades_df):
        '''
        计算平均每笔收益、平均持仓时间、交易次数、盈亏比、胜率
        输出格式为dataframe
        '''        
        open_trades = trades_df[trades_df['open_close'] == 'OPEN']
        close_trades = trades_df[trades_df['open_close'] == 'CLOSE']
        open_trades.reset_index(inplace = True)
        close_trades.reset_index(inplace = True)
        ret_long = close_trades[close_trades['LS'] == 'LONG']['price'] \
                   - open_trades[open_trades['LS'] == 'LONG']['price']
        ret_long.index = open_trades[open_trades['LS'] == 'LONG']['ts']
        ret_short = open_trades[open_trades['LS'] == 'SHORT']['price'] \
                   - close_trades[close_trades['LS'] == 'SHORT']['price']
        ret_short.index = open_trades[open_trades['LS'] == 'SHORT']['ts']
        ret_all = pd.concat([ret_long,ret_short])
        ret_all = ret_all.sort_index()

        average_ret = {'total':np.mean(ret_all),
                    'long':np.mean(ret_long),
                    'short':np.mean(ret_short)}
        
        ret_per_size = pd.DataFrame({'ret_long':ret_long,
                                    'ret_short':ret_short,
                                    'ret_all':ret_all
                                    })
        ret_per_size = ret_per_size.fillna(0)
        
        total_profit = ret_per_size[ret_per_size>0].sum(axis = 0)
        total_coss = - ret_per_size[ret_per_size<0].sum(axis = 0)
        ProfitCossRatio = total_profit/total_coss
        
        
        ProfitCossRatio = {'total':ProfitCossRatio['ret_all'],
                        'long':ProfitCossRatio['ret_long'],
                        'short':ProfitCossRatio['ret_short']}
        
        total_len = len(trades_df)
        long_len = len(trades_df[trades_df['LS'] == 'LONG'])
        short_len = len(trades_df[trades_df['LS'] == 'SHORT'])
        #一笔交易、先买后买算作两次，或许是因为买卖都有交易费
        trades_count = {'total' : total_len, 'long' : long_len,'short' : short_len}
        
        count_profit = ret_per_size[ret_per_size>0].count(axis = 0)
        count_coss =  ret_per_size[ret_per_size<0].count(axis = 0)
        ProfitRate = count_profit/(count_coss+count_profit)
        ProfitRate = ProfitRate
        
        ProfitRate = {'total':ProfitRate['ret_all'],
                    'long':ProfitRate['ret_long'],
                    'short':ProfitRate['ret_short']}
        
        trades_time = trades_df[['LS','open_close']]
        trades_time['datetime'] = trades_time.index.strftime("%Y-%m-%d %H:%M:%S")   #series，str
        trades_time.index = trades_time.index.strftime("%Y-%m-%d %H:%M:%S")
        trades_time.index = pd.to_datetime(trades_time.index)                       #timestamp
        close_time = trades_time[trades_time['open_close'] == 'CLOSE']
        open_time = trades_time[trades_time['open_close'] == 'OPEN']
        close_time['pos_time'] = close_time.index - open_time.index
        for i in range(0,len(open_time)):
            if open_time['datetime'][i][-8:]<'11:30:00' and close_time['datetime'][i][-8:]>'13:30:00':
                close_time['pos_time'][i] = close_time['pos_time'][i] - pd.to_timedelta(2,'h')
        pos_time = close_time.drop(labels = ['datetime' , 'open_close'],axis = 1)
        total_time = pd.Timedelta(np.mean(pos_time['pos_time'].values),'m')   #这里没有剔除中午的停盘时间
        long_time = pd.Timedelta(np.mean(pos_time[pos_time['LS'] == 'LONG']['pos_time'].values),'m')
        short_time = pd.Timedelta(np.mean(pos_time[pos_time['LS'] == 'SHORT']['pos_time'].values),'m')
        average_pos_time = {'total':total_time,'long':long_time,'short':short_time}
        ret_assese_df = pd.DataFrame(dict(average_ret = average_ret,
                                        ProfitCossRatio = ProfitCossRatio,
                                        ProfitRate = ProfitRate,
                                        trades_count = trades_count,
                                        average_pos_time = average_pos_time
                                        ))
        return ret_assese_df
    


    

    
