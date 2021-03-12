# -*- coding: utf-8 -*-
# @Time     : 2020/07/24 
# @Author   ：Li Wenting
# @File     : ResultAssese.py
# @Software : 

import numpy as np
import pandas as pd
import algoqi.perfeval.trades_analysis as PTA   #分别计算long，short仓位累计收益
import algoqi.data.plotutils as P               #绘制累计收益图
from algoqi.data import D, plotutils
D.switch_zxzx_client(access_key='e7e2de63f95674632824ed6b2be8dd1f', secret_key='d43ca617fe7048e4ccfb158dde8e1c32')
D.load()
from market_timing_lab import MeanReversion
from highcharts import Highstock
from HighchartConfig import *


class ResultAssese:
    '''
    type(trades_df.index[0]) : pandas._libs.tslibs.timestamps.Timestamp
    '''
#     def pos_all(trades_df):
#         '''
#         计算整个回测期间仓位的累计收益，由于主力合约发生转换后，新合约的累计收益从
#         0开始，所以，新合约的累计收益要在上一个主力合约期末累计收益基础上计算
#         '''

#         pos_list = []                                                #定义空列表
#         code =  trades_df['sym'].values.tolist()
#         code_list = sorted(list(set(code)),key = code.index)         #去重并保持原有顺序
#         acc_ret = [0,0,0]                                            #初始化
#         for i in range(0,len(code_list)):
#             pos = PTA.calc_pnl_all(trades_df[trades_df['sym'] == code_list[i]],{})
#             if not(code_list[i]+' Long' in pos.columns):
#                 pos[code_list[i]+' Long'] = 0.0
#             if not(code_list[i]+' Short' in pos.columns):
#                 pos[code_list[i]+' Short'] = 0.0
                
#             print('111111\n',pos)
#             print('*******')
#             #xhq modify
            
#             pos = pos+acc_ret                                        #在上一个合约累计收益基础上计算仓位的累计收益
# #             pos = pos + acc_ret[:len(pos.columns)]
#             pos = pos.rename(columns = 
#                             {code_list[i]+' Long':'Long',
#                             code_list[i]+' Short':'Short',
#                             })
#             print(pos)
#             pos['Short'][-1]
#             acc_ret = [pos['Long'][-1],pos['Short'][-1],pos['acc_pnl'][-1]]
#             pos['sym'] = code_list[i]
#             pos_list.append(pos)
#         pos_df = pd.concat(pos_list,sort = True)
#         return pos_df

    def pos_all(trades_df):
        '''
        计算整个回测期间仓位的累计收益，由于主力合约发生转换后，新合约的累计收益从
        0开始，所以，新合约的累计收益要在上一个主力合约期末累计收益基础上计算
        '''

        pos_list = []                                                #定义空列表
        code =  trades_df['sym'].values.tolist()
        code_list = sorted(list(set(code)),key = code.index)         #去重并保持原有顺序
        acc_ret = [0,0,0]                                            #初始化
        for i in range(0,len(code_list)):
            pos = PTA.calc_pnl_all(trades_df[trades_df['sym'] == code_list[i]],{})
            #xhq modify
            if not(code_list[i]+' Long' in pos.columns):
                pos[code_list[i]+' Long'] = 0.0
            if not(code_list[i]+' Short' in pos.columns):
                pos[code_list[i]+' Short'] = 0.0
            ###



            pos = pos+acc_ret                                        #在上一个合约累计收益基础上计算仓位的累计收益

            pos = pos.rename(columns = 
                            {code_list[i]+' Long':'Long',
                            code_list[i]+' Short':'Short',
                            })
            #xhq modify
            #acc_ret = [pos['Long'][-1],pos['Short'][-1],pos['acc_pnl'][-1]]
            acc_ret = [pos['Long'].iloc[-1],pos['Short'].iloc[-1],pos['acc_pnl'].iloc[-1]]
            pos['sym'] = code_list[i]
            pos_list.append(pos)
        pos_df = pd.concat(pos_list,sort = True)
        return pos_df

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
    
    def FigAccuRet(pos_df):
        '''
        绘制累计收益图，不区分long和short【有误】
        '''
        return P.plot_timeseries(pos_df['acc_pnl'])

    def FigAccuRet_L(pos_df):
        '''
        绘制long仓位累计收益图【有误】
        '''
        return P.plot_timeseries(pos_df['Long'])
    
    def FigAccuRet_S(pos_df):
        '''
        绘制short仓位累计收益图【有误】
        '''
        return P.plot_timeseries(pos_df['Short'])

    def FigAccuRet(ret_df):
        '''
        将long,short,all的累计收益图绘制在一个图表上
        '''
        ret_cumsum0 = ret_df[['ret_long','ret_short','ret_all']].cumsum()
        H = Highstock(offline=True)
        H = add_offline_mode(H)
        options = options_for_line(title = '累计收益图',y_title = '累计收益')
        H.set_dict_options(options)
        ret_cumsum0['datetime']= ret_cumsum0.index 
        ret_LS_list = ret_cumsum0[['datetime','ret_all']].values.tolist()
        ret_L_list = ret_cumsum0[['datetime','ret_long']].values.tolist()
        ret_S_list = ret_cumsum0[['datetime','ret_short']].values.tolist()
        H.add_data_set(ret_LS_list, 'line',name = 'ret_all')
        H.add_data_set(ret_L_list, 'line',name = 'ret_long')
        H.add_data_set(ret_S_list, 'line',name = 'ret_short')
        return H 
    
#     def FigAccuRet(ret_df,title = '累计收益图',y_title = '累计收益'):
#         '''
#         将long,short,all的累计收益图绘制在一个图表上
#         '''
#         H = Highstock(offline=True)
#         H = add_offline_mode(H)
#         for direction in ['ret_all','ret_long','ret_short']:
#             pnl_list = ret_df[direction].dropna().cumsum().reset_index().values.tolist()
#             H.add_data_set(pnl_list,'line',direction,lineWidth = 1)
#             locals()[direction+'_list'] = pnl_list   # 动态创建变量名
#         H.set_dict_options(options_for_line(title,y_title))
#         return H
    
    def FigKline(code:str,start:str,end:str):
        '''
        绘制K线图
        '''
        class ContFutureSymbolFilter(D.FutContContractFilter):
            @staticmethod
            def future_suffix_replace(symbol_str: str):
                return symbol_str if '.CFE' not in symbol_str[0] else [symbol_str[0].replace(".CFE", ".CF")]

            def symbols_during(self, start_dt: str, end_dt: str):
                main_contracts_df = self._query_main_contract(symbols=self.symbols, start=start_dt, end=end_dt)
                if not main_contracts_df.empty:
                    cont_list = []
                    for i in range(len(main_contracts_df)):
                        sub_cont = (main_contracts_df.iloc[i].symbol, main_contracts_df.iloc[i].start,
                                    main_contracts_df.iloc[i].end, self.future_suffix_replace([main_contracts_df.iloc[i].mapping_symbol]))
                        cont_list.append(sub_cont)
                return cont_list
        
        prices = D.query_tsdata(datasource='future_kline_1min', symbols=ContFutureSymbolFilter(code), fields='*', start=start, end=end)
        prices_list = []
        for df in prices:
#             #xhq modify
#             df.index = pd.Series(df.index).shift(-1)
#             df = df.iloc[:-1,:]
#             ###
            prices_list.append(df)
        prices_df = pd.concat(prices_list)
        
        prices = prices_df[['Symbol', 'open', 'high', 'low', 'close']]
        prices.reset_index(inplace=True)
        prices = prices.rename(columns={'index':'DATETIME', 'Symbol': 'code'})
        H = Highstock(offline=True)
        def add_offline_mode(H):
            highstock_css = ["http://orientlab.orientsec.com.cn:30080/static/highcharts/highslide.css"]
            highstock_js = ["http://orientlab.orientsec.com.cn:30080/static/highcharts/jquery.min.js",
                            "http://orientlab.orientsec.com.cn:30080/static/highcharts/highstock.js",
                            "http://orientlab.orientsec.com.cn:30080/static/highcharts/exporting.js",
                            "http://orientlab.orientsec.com.cn:30080/static/highcharts/highcharts-more.js",
                        ]
            H.JSsource.clear()
            H.CSSsource.clear()
            H.add_CSSsource(highstock_css)
            H.add_JSsource(highstock_js)
            return H
        H = add_offline_mode(H)
        
        prices_list = prices[['DATETIME', 'open', 'high', 'low', 'close']].values.tolist()
        H.add_data_set(prices_list, 'candlestick', '{} Prices'.format(code), id = 'dataseries')
        
        title = 'IC00.CFE'
        width = '200px'
        valueDecimals = 4
        
        options = {
                    'rangeSelector': {
                        'selected': 0
                    },

                    'title': {
                        'text': title
                    },
                    'tooltip': {
                        'style': {
                            'width': width
                        },
                        'valueDecimals': valueDecimals,
                        'shared': True
                    },
                    'yAxis': {
                        'title': {
                            'text': 'OHLC'
                        }
                    },
                    'legend':{
                        'enabled':True,
                        'align':'center',
                    },
                    'plotOptions': {
                        'candlestick': {
                            'color': 'green',
                            'upColor': 'red',
                        }
                    },
                }
        H.set_dict_options(options)
        return H
    
    def FigTradesSig(code:str,start:str,end:str,trades_df):
        '''
        在K线图的基础上标记开平仓交易记录
        '''
        class ContFutureSymbolFilter(D.FutContContractFilter):
            @staticmethod
            def future_suffix_replace(symbol_str: str):
                return symbol_str if '.CFE' not in symbol_str[0] else [symbol_str[0].replace(".CFE", ".CF")]

            def symbols_during(self, start_dt: str, end_dt: str):
                main_contracts_df = self._query_main_contract(symbols=self.symbols, start=start_dt, end=end_dt)
                if not main_contracts_df.empty:
                    cont_list = []
                    for i in range(len(main_contracts_df)):
                        sub_cont = (main_contracts_df.iloc[i].symbol, main_contracts_df.iloc[i].start,
                                    main_contracts_df.iloc[i].end, self.future_suffix_replace([main_contracts_df.iloc[i].mapping_symbol]))
                        cont_list.append(sub_cont)
                return cont_list
        
        prices = D.query_tsdata(datasource='future_kline_1min', symbols=ContFutureSymbolFilter(code), fields='*', start=start, end=end)
        prices_list = []
        for df in prices:
#             #xhq modify
#             df.index = pd.Series(df.index).shift(-1)
#             df = df.iloc[:-1,:]
#             ###
            prices_list.append(df)
        prices_df = pd.concat(prices_list)
        
        prices = prices_df[['Symbol', 'open', 'high', 'low', 'close']]
        prices.reset_index(inplace=True)
        prices = prices.rename(columns={'index':'DATETIME', 'Symbol': 'code'})
        H = Highstock(offline=True)
        def add_offline_mode(H):
            highstock_css = ["http://orientlab.orientsec.com.cn:30080/static/highcharts/highslide.css"]
            highstock_js = ["http://orientlab.orientsec.com.cn:30080/static/highcharts/jquery.min.js",
                            "http://orientlab.orientsec.com.cn:30080/static/highcharts/highstock.js",
                            "http://orientlab.orientsec.com.cn:30080/static/highcharts/exporting.js",
                            "http://orientlab.orientsec.com.cn:30080/static/highcharts/highcharts-more.js",
                        ]
            H.JSsource.clear()
            H.CSSsource.clear()
            H.add_CSSsource(highstock_css)
            H.add_JSsource(highstock_js)
            return H
        H = add_offline_mode(H)
        
        prices_list = prices[['DATETIME', 'open', 'high', 'low', 'close']].values.tolist()
        H.add_data_set(prices_list, 'candlestick', '{} Prices'.format(code), id = 'dataseries')
        
        title = 'IC00.CFE'
        width = '200px'
        valueDecimals = 4
        
        options = {
                    'rangeSelector': {
                        'selected': 0
                    },

                    'title': {
                        'text': title
                    },
                    'tooltip': {
                        'style': {
                            'width': width
                        },
                        'valueDecimals': valueDecimals,
                        'shared': True
                    },
                    'yAxis': {
                        'title': {
                            'text': 'OHLC'
                        }
                    },
                    'legend':{
                        'enabled':True,
                        'align':'center',
                    },
                    'plotOptions': {
                        'candlestick': {
                            'color': 'green',
                            'upColor': 'red',
                        }
                    },
                }
        H.set_dict_options(options)
        
        trades_df['datetime'] = trades_df.index.strftime("%Y-%m-%d %H:%M:%S")     #统一时间格式
        trades_df['datetime'] = pd.to_datetime(trades_df['datetime'])
        long_open = trades_df[(trades_df['open_close'] == 'OPEN')&(trades_df['LS'] == 'LONG')]
        long_close = trades_df[(trades_df['open_close'] == 'CLOSE')&(trades_df['LS'] == 'LONG')]
        short_open = trades_df[(trades_df['open_close'] == 'OPEN')&(trades_df['LS'] == 'SHORT')]
        short_close = trades_df[(trades_df['open_close'] == 'CLOSE')&(trades_df['LS'] == 'SHORT')]
        long_open_time = long_open.datetime.tolist()
        long_close_time = long_close.datetime.tolist()
        short_open_time = short_open.datetime.tolist()
        short_close_time = short_close.datetime.tolist()
        #标识位置
        LO = [dict(x=long_open_time[i],title='LO',text = 'LO,price:{}'.format(long_open['price'][i])) \
            for i in range(0,len(long_open_time))]
        LC = [dict(x=long_close_time[i],title='LC',text = 'LC,price:{}'.format(long_close['price'][i]))\
            for i in range(0,len(long_close_time))]
        SO = [dict(x=short_open_time[i],title='SO',text = 'SO,price:{}'.format(short_open['price'][i]))\
            for i in range(0,len(short_open_time))]
        SC = [dict(x=short_close_time[i],title='SC',text = 'SC,price:{}'.format(short_close['price'][i]))\
            for i in range(0,len(short_close_time))]
        #标识形状
        H.add_data_set(LO,'flags',style = dict(fontSize = '0.6em'),shape = 'circlepin',onSeries = 'dataseries',name = 'LO')
        H.add_data_set(LC,'flags',style = dict(fontSize = '0.6em'),shape = 'circlepin',onSeries = 'dataseries',name = 'LC')
        H.add_data_set(SO,'flags',style = dict(fontSize = '0.6em'),shape = 'circlepin',onSeries = 'dataseries',name = 'SO')
        H.add_data_set(SC,'flags',style = dict(fontSize = '0.6em'),shape = 'circlepin',onSeries = 'dataseries',name = 'SC')
        return H
    
    def FigTradesSig_update(code:str,start:str,end:str,trades_df,logs_df):
        '''
        在K线图的基础上标记开平仓交易记录,区分开平仓和止损平仓
        '''
        class ContFutureSymbolFilter(D.FutContContractFilter):
            @staticmethod
            def future_suffix_replace(symbol_str: str):
                return symbol_str if '.CFE' not in symbol_str[0] else [symbol_str[0].replace(".CFE", ".CF")]

            def symbols_during(self, start_dt: str, end_dt: str):
                main_contracts_df = self._query_main_contract(symbols=self.symbols, start=start_dt, end=end_dt)
                if not main_contracts_df.empty:
                    cont_list = []
                    for i in range(len(main_contracts_df)):
                        sub_cont = (main_contracts_df.iloc[i].symbol, main_contracts_df.iloc[i].start,
                                    main_contracts_df.iloc[i].end, self.future_suffix_replace([main_contracts_df.iloc[i].mapping_symbol]))
                        cont_list.append(sub_cont)
                return cont_list
        
        prices = D.query_tsdata(datasource='future_kline_1min', symbols=ContFutureSymbolFilter(code), fields='*', start=start, end=end)
        prices_list = []
        for df in prices:
#             #xhq modify
#             df.index = pd.Series(df.index).shift(-1)
#             df = df.iloc[:-1,:]
#             ###
            prices_list.append(df)
        prices_df = pd.concat(prices_list)
        
        prices = prices_df[['Symbol', 'open', 'high', 'low', 'close']]
        prices.reset_index(inplace=True)
        prices = prices.rename(columns={'index':'DATETIME', 'Symbol': 'code'})
        H = Highstock(offline=True)
        def add_offline_mode(H):
            highstock_css = ["http://orientlab.orientsec.com.cn:30080/static/highcharts/highslide.css"]
            highstock_js = ["http://orientlab.orientsec.com.cn:30080/static/highcharts/jquery.min.js",
                            "http://orientlab.orientsec.com.cn:30080/static/highcharts/highstock.js",
                            "http://orientlab.orientsec.com.cn:30080/static/highcharts/exporting.js",
                            "http://orientlab.orientsec.com.cn:30080/static/highcharts/highcharts-more.js",
                        ]
            H.JSsource.clear()
            H.CSSsource.clear()
            H.add_CSSsource(highstock_css)
            H.add_JSsource(highstock_js)
            return H
        H = add_offline_mode(H)
        
        prices_list = prices[['DATETIME', 'open', 'high', 'low', 'close']].values.tolist()
        H.add_data_set(prices_list, 'candlestick', '{} Prices'.format(code), id = 'dataseries')
        
        title = 'IC00.CFE'
        width = '200px'
        valueDecimals = 4
        
        options = {
                    'rangeSelector': {
                        'selected': 0
                    },

                    'title': {
                        'text': title
                    },
                    'tooltip': {
                        'style': {
                            'width': width
                        },
                        'valueDecimals': valueDecimals,
                        'shared': True
                    },
                    'yAxis': {
                        'title': {
                            'text': 'OHLC'
                        }
                    },
                    'legend':{
                        'enabled':True,
                        'align':'center',
                    },
                    'plotOptions': {
                        'candlestick': {
                            'color': 'green',
                            'upColor': 'red',
                        }
                    },
                }
        H.set_dict_options(options)
        
        trades_df['datetime'] = trades_df.index.strftime("%Y-%m-%d %H:%M:%S")     #统一时间格式
        trades_df['datetime'] = pd.to_datetime(trades_df['datetime'])
        long_open = trades_df[(trades_df['open_close'] == 'OPEN')&(trades_df['LS'] == 'LONG')]
#         long_close = trades_df[(trades_df['open_close'] == 'CLOSE')&(trades_df['LS'] == 'LONG')]
        short_open = trades_df[(trades_df['open_close'] == 'OPEN')&(trades_df['LS'] == 'SHORT')]
#         short_close = trades_df[(trades_df['open_close'] == 'CLOSE')&(trades_df['LS'] == 'SHORT')]
        long_open_time = long_open.datetime.tolist()
#         long_close_time = long_close.datetime.tolist()
        short_open_time = short_open.datetime.tolist()
#         short_close_time = short_close.datetime.tolist()
        
    

        logs_df = pd.DataFrame(logs_df).copy()
        logs_df.reset_index(inplace = True)
        logs_df.rename({'0':'datetime','1':'log'},axis = 1,inplace = True)
        logs_df.rename({0:'datetime',1:'log'},axis = 1,inplace = True)
        logs_df['datetime'] = logs_df['datetime'].apply(lambda x:x.strftime("%Y-%m-%d %H:%M:%S"))     #统一时间格式
        logs_df['datetime'] = pd.to_datetime(logs_df['datetime'])
        logs_df['logs_shorter'] = logs_df['log'].apply(lambda x:x[:-7])

        
        stop_lc = logs_df[logs_df['logs_shorter'] == '破底CL']
        stop_sc = logs_df[logs_df['logs_shorter'] == '破顶CS']
        normal_lc = logs_df[logs_df['logs_shorter'] == 'CL']
        normal_sc = logs_df[logs_df['logs_shorter'] == 'CS']
        end_lc = logs_df[logs_df['logs_shorter'] == 'end_CL']
        end_sc = logs_df[logs_df['logs_shorter'] == 'end_CS']

        stop_lc_time = stop_lc.datetime.to_list()
        stop_sc_time = stop_sc.datetime.to_list()
        normal_lc_time = normal_lc.datetime.to_list()
        normal_sc_time = normal_sc.datetime.to_list()
        end_lc_time = end_lc.datetime.to_list()
        end_sc_time = end_sc.datetime.to_list()
        
        #标识位置
        LO = [dict(x=long_open_time[i],title='LO',text = 'LO,price:{}'.format(long_open['price'][i])) \
            for i in range(0,len(long_open_time))]
        SO = [dict(x=short_open_time[i],title='SO',text = 'SO,price:{}'.format(short_open['price'][i]))\
            for i in range(0,len(short_open_time))]
        
        NLC = [dict(x=normal_lc_time[i],title='NLC',text = 'NLC,price:{}'.format(normal_lc['log'].iloc[i][-6:]))\
            for i in range(0,len(normal_lc_time))]
        NSC = [dict(x=normal_sc_time[i],title='NSC',text = 'NSC,price:{}'.format(normal_sc['log'].iloc[i][-6:]))\
            for i in range(0,len(normal_sc_time))]
        SLC = [dict(x=stop_lc_time[i],title='SLC',text = 'SLC,price:{}'.format(stop_lc['log'].iloc[i][-6:]))\
            for i in range(0,len(stop_lc_time))]
        SSC = [dict(x=stop_sc_time[i],title='SSC',text = 'SSC,price:{}'.format(stop_sc['log'].iloc[i][-6:]))\
            for i in range(0,len(stop_sc_time))]
        ELC = [dict(x=end_lc_time[i],title='ELC',text = 'ELC,price:{}'.format(end_lc['log'].iloc[i][-6:]))\
            for i in range(0,len(end_lc_time))]
        ESC = [dict(x=end_sc_time[i],title='ESC',text = 'ESC,price:{}'.format(end_sc['log'].iloc[i][-6:]))\
            for i in range(0,len(end_sc_time))]

        #标识形状
        H.add_data_set(LO,'flags',style = dict(fontSize = '0.6em'),shape = 'circlepin',onSeries = 'dataseries',name = 'LO')
        H.add_data_set(SO,'flags',style = dict(fontSize = '0.6em'),shape = 'circlepin',onSeries = 'dataseries',name = 'SO')
        
        H.add_data_set(NLC,'flags',style = dict(fontSize = '0.6em'),shape = 'squarepin',onSeries = 'dataseries',name = 'NLC')
        H.add_data_set(NSC,'flags',style = dict(fontSize = '0.6em'),shape = 'squarepin',onSeries = 'dataseries',name = 'NSC')
        H.add_data_set(SLC,'flags',style = dict(fontSize = '0.6em'),shape = 'squarepin',onSeries = 'dataseries',name = 'SLC')
        H.add_data_set(SSC,'flags',style = dict(fontSize = '0.6em'),shape = 'squarepin',onSeries = 'dataseries',name = 'SSC')
        H.add_data_set(ELC,'flags',style = dict(fontSize = '0.6em'),shape = 'squarepin',onSeries = 'dataseries',name = 'ELC')
        H.add_data_set(ESC,'flags',style = dict(fontSize = '0.6em'),shape = 'squarepin',onSeries = 'dataseries',name = 'ESC')

        return H
    
    def FigRetPerSize(ret_per_size):
        '''
        Plot bar figure of return per size for long and short seperately
        Parameters:DataFrame
        return:
        '''
        H = Highstock(offline=True)
        def add_offline_mode(H):
            highstock_css = ["http://orientlab.orientsec.com.cn:30080/static/highcharts/highslide.css"]
            highstock_js = ["http://orientlab.orientsec.com.cn:30080/static/highcharts/jquery.min.js",
                            "http://orientlab.orientsec.com.cn:30080/static/highcharts/highstock.js",
                            "http://orientlab.orientsec.com.cn:30080/static/highcharts/exporting.js",
                            "http://orientlab.orientsec.com.cn:30080/static/highcharts/highcharts-more.js",
                        ]
            H.JSsource.clear()
            H.CSSsource.clear()
            H.add_CSSsource(highstock_css)
            H.add_JSsource(highstock_js)
            return H
        H = add_offline_mode(H)
        ret_per_size['datetime']= ret_per_size.index.strftime("%Y-%m-%d %H:%M:%S")     #统一时间格式
        ret_per_size['datetime'] = pd.to_datetime(ret_per_size['datetime'])
        ret_long = ret_per_size[['datetime','ret_long']]
        ret_long[ret_long.ret_long == 0] = np.nan
        ret_long = ret_long.dropna()
        ret_L_list = ret_long.values.tolist()
        ret_short = ret_per_size[['datetime','ret_short']]
        ret_short[ret_short.ret_short == 0] = np.nan
        ret_short = ret_short.dropna()
        ret_S_list = ret_short.values.tolist()
        H.add_data_set(ret_L_list, 'column',name = 'ret_long',color = '#CD5C5C')
        H.add_data_set(ret_S_list, 'column',name = 'ret_short',color = '#90EE90')
        options = {
                    'rangeSelector': {
                        'selected': 0
                    },
                    
                    'title': {
                        'text': 'Return Per Size'
                    },
                    'tooltip': {
                        'style': {
                            'width': '200px'
                        },
                        'valueDecimals':4,
                        'shared': True
                    },
                    'legend':{
                        'enabled':True,
                        'align':'center',
                    },
                    'yAxis': {
                        'title': {
                            'text': 'Value'
                        }
                    }
                }
        H.set_dict_options(options)

        
        return H

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
    
    def FigRetPerSize_update(ret_per_size,logs_df):
        '''
        加上平仓标识符，并且将return per size的时间戳放在平仓时间
        Plot bar figure of return per size for long and short seperately
        Parameters:DataFrame
        return:
        '''
        H = Highstock(offline=True)
        def add_offline_mode(H):
            highstock_css = ["http://orientlab.orientsec.com.cn:30080/static/highcharts/highslide.css"]
            highstock_js = ["http://orientlab.orientsec.com.cn:30080/static/highcharts/jquery.min.js",
                            "http://orientlab.orientsec.com.cn:30080/static/highcharts/highstock.js",
                            "http://orientlab.orientsec.com.cn:30080/static/highcharts/exporting.js",
                            "http://orientlab.orientsec.com.cn:30080/static/highcharts/highcharts-more.js",
                        ]
            H.JSsource.clear()
            H.CSSsource.clear()
            H.add_CSSsource(highstock_css)
            H.add_JSsource(highstock_js)
            return H
        H = add_offline_mode(H)
        ret_per_size['datetime']= ret_per_size.index.strftime("%Y-%m-%d %H:%M:%S")     #统一时间格式
        ret_per_size['datetime'] = pd.to_datetime(ret_per_size['datetime'])
        ret_long = ret_per_size[['datetime','ret_long']]
        ret_long[ret_long.ret_long == 0] = np.nan
        ret_long = ret_long.dropna()
        ret_L_list = ret_long.values.tolist()
        ret_short = ret_per_size[['datetime','ret_short']]
        ret_short[ret_short.ret_short == 0] = np.nan
        ret_short = ret_short.dropna()
        ret_S_list = ret_short.values.tolist()
        H.add_data_set(ret_L_list, 'column',name = 'ret_long',color = '#CD5C5C')
        H.add_data_set(ret_S_list, 'column',name = 'ret_short',color = '#90EE90')
        options = {
                    'rangeSelector': {
                        'selected': 0
                    },
                    
                    'title': {
                        'text': 'Return Per Size'
                    },
                    'tooltip': {
                        'style': {
                            'width': '200px'
                        },
                        'valueDecimals':4,
                        'shared': True
                    },
                    'legend':{
                        'enabled':True,
                        'align':'center',
                    },
                    'yAxis': {
                        'title': {
                            'text': 'Value'
                        }
                    }
                }
        H.set_dict_options(options)
        
   #平仓标识
        logs_df = pd.DataFrame(logs_df).copy()
        logs_df.reset_index(inplace = True)
        logs_df.rename({'0':'datetime','1':'log'},axis = 1,inplace = True)
        logs_df.rename({0:'datetime',1:'log'},axis = 1,inplace = True)
        logs_df['datetime'] = logs_df['datetime'].apply(lambda x:x.strftime("%Y-%m-%d %H:%M:%S"))     #统一时间格式
        logs_df['datetime'] = pd.to_datetime(logs_df['datetime'])
        logs_df['logs_shorter'] = logs_df['log'].apply(lambda x:x[:-7])

        
        stop_lc = logs_df[logs_df['logs_shorter'] == '破底CL']
        stop_sc = logs_df[logs_df['logs_shorter'] == '破顶CS']
        normal_lc = logs_df[logs_df['logs_shorter'] == 'CL']
        normal_sc = logs_df[logs_df['logs_shorter'] == 'CS']
        end_lc = logs_df[logs_df['logs_shorter'] == 'end_CL']
        end_sc = logs_df[logs_df['logs_shorter'] == 'end_CS']

        stop_lc_time = stop_lc.datetime.to_list()
        stop_sc_time = stop_sc.datetime.to_list()
        normal_lc_time = normal_lc.datetime.to_list()
        normal_sc_time = normal_sc.datetime.to_list()
        end_lc_time = end_lc.datetime.to_list()
        end_sc_time = end_sc.datetime.to_list()
        
        #标识位置
        
        NLC = [dict(x=normal_lc_time[i],title='NLC',text = 'NLC,price:{}'.format(normal_lc['log'].iloc[i][-6:]))\
            for i in range(0,len(normal_lc_time))]
        NSC = [dict(x=normal_sc_time[i],title='NSC',text = 'NSC,price:{}'.format(normal_sc['log'].iloc[i][-6:]))\
            for i in range(0,len(normal_sc_time))]
        SLC = [dict(x=stop_lc_time[i],title='SLC',text = 'SLC,price:{}'.format(stop_lc['log'].iloc[i][-6:]))\
            for i in range(0,len(stop_lc_time))]
        SSC = [dict(x=stop_sc_time[i],title='SSC',text = 'SSC,price:{}'.format(stop_sc['log'].iloc[i][-6:]))\
            for i in range(0,len(stop_sc_time))]
        ELC = [dict(x=end_lc_time[i],title='ELC',text = 'ELC,price:{}'.format(end_lc['log'].iloc[i][-6:]))\
            for i in range(0,len(end_lc_time))]
        ESC = [dict(x=end_sc_time[i],title='ESC',text = 'ESC,price:{}'.format(end_sc['log'].iloc[i][-6:]))\
            for i in range(0,len(end_sc_time))]

        #标识形状
        H.add_data_set(NLC,'flags',style = dict(fontSize = '0.6em'),shape = 'squarepin',onSeries = 'dataseries',name = 'NLC')
        H.add_data_set(NSC,'flags',style = dict(fontSize = '0.6em'),shape = 'squarepin',onSeries = 'dataseries',name = 'NSC')
        H.add_data_set(SLC,'flags',style = dict(fontSize = '0.6em'),shape = 'squarepin',onSeries = 'dataseries',name = 'SLC')
        H.add_data_set(SSC,'flags',style = dict(fontSize = '0.6em'),shape = 'squarepin',onSeries = 'dataseries',name = 'SSC')
        H.add_data_set(ELC,'flags',style = dict(fontSize = '0.6em'),shape = 'squarepin',onSeries = 'dataseries',name = 'ELC')
        H.add_data_set(ESC,'flags',style = dict(fontSize = '0.6em'),shape = 'squarepin',onSeries = 'dataseries',name = 'ESC')
        
        return H
    
    def FigParting(code:str,start:str,end:str,trades_df):
        '''
        在k线上标记顶底
        '''
        class ContFutureSymbolFilter(D.FutContContractFilter):
            @staticmethod
            def future_suffix_replace(symbol_str: str):
                return symbol_str if '.CFE' not in symbol_str[0] else [symbol_str[0].replace(".CFE", ".CF")]

            def symbols_during(self, start_dt: str, end_dt: str):
                main_contracts_df = self._query_main_contract(symbols=self.symbols, start=start_dt, end=end_dt)
                if not main_contracts_df.empty:
                    cont_list = []
                    for i in range(len(main_contracts_df)):
                        sub_cont = (main_contracts_df.iloc[i].symbol, main_contracts_df.iloc[i].start,
                                    main_contracts_df.iloc[i].end, self.future_suffix_replace([main_contracts_df.iloc[i].mapping_symbol]))
                        cont_list.append(sub_cont)
                return cont_list

        prices = D.query_tsdata(datasource='future_kline_1min', symbols=ContFutureSymbolFilter(code), fields='*', start=start, end=end)
        prices_list = []
        for df in prices:
#             #xhq modify
#             df.index = df.index.shift(-1)
#             df = df.iloc[:-1,:]
#             ###
            prices_list.append(df)
        prices_df = pd.concat(prices_list)

        prices = prices_df[['Symbol', 'open', 'high', 'low', 'close']]
        prices.reset_index(inplace=True)
        prices = prices.rename(columns={'index':'DATETIME', 'Symbol': 'code'})
        H = Highstock(offline=True)
        def add_offline_mode(H):
            highstock_css = ["http://orientlab.orientsec.com.cn:30080/static/highcharts/highslide.css"]
            highstock_js = ["http://orientlab.orientsec.com.cn:30080/static/highcharts/jquery.min.js",
                            "http://orientlab.orientsec.com.cn:30080/static/highcharts/highstock.js",
                            "http://orientlab.orientsec.com.cn:30080/static/highcharts/exporting.js",
                            "http://orientlab.orientsec.com.cn:30080/static/highcharts/highcharts-more.js",
                           ]
            H.JSsource.clear()
            H.CSSsource.clear()
            H.add_CSSsource(highstock_css)
            H.add_JSsource(highstock_js)
            return H
        H = add_offline_mode(H)

        prices_list = prices[['DATETIME', 'open', 'high', 'low', 'close']].values.tolist()
        H.add_data_set(prices_list, 'candlestick', '{} Prices'.format(code), id = 'dataseries')

        title = 'IC00.CFE'
        width = '200px'
        valueDecimals = 4

        options = {
                    'rangeSelector': {
                        'selected': 0
                    },

                    'title': {
                        'text': title
                    },
                    'tooltip': {
                        'style': {
                            'width': width
                        },
                        'valueDecimals': valueDecimals,
                        'shared': True
                    },
                    'yAxis': {
                        'title': {
                            'text': 'OHLC'
                        }
                    },
                    'legend':{
                        'enabled':True,
                        'align':'center',
                    },
                    'plotOptions': {
                        'candlestick': {
                            'color': 'green',
                            'upColor': 'red',
                        }
                    },
                }
        H.set_dict_options(options)

        trades_df['datetime'] = trades_df.index.strftime("%Y-%m-%d %H:%M:%S")     #统一时间格式
        trades_df['datetime'] = pd.to_datetime(trades_df['datetime'])
        long_open = trades_df[(trades_df['open_close'] == 'OPEN')&(trades_df['LS'] == 'LONG')]
        long_close = trades_df[(trades_df['open_close'] == 'CLOSE')&(trades_df['LS'] == 'LONG')]
        short_open = trades_df[(trades_df['open_close'] == 'OPEN')&(trades_df['LS'] == 'SHORT')]
        short_close = trades_df[(trades_df['open_close'] == 'CLOSE')&(trades_df['LS'] == 'SHORT')]
        long_open_time = long_open.datetime.tolist()
        long_close_time = long_close.datetime.tolist()
        short_open_time = short_open.datetime.tolist()
        short_close_time = short_close.datetime.tolist()

        LO = [dict(x=long_open_time[i],title='LO',text = 'LO,price:{}'.format(long_open['price'][i])) \
              for i in range(0,len(long_open_time))]
        LC = [dict(x=long_close_time[i],title='LC',text = 'LC,price:{}'.format(long_close['price'][i]))\
              for i in range(0,len(long_close_time))]
        SO = [dict(x=short_open_time[i],title='SO',text = 'SO,price:{}'.format(short_open['price'][i]))\
              for i in range(0,len(short_open_time))]
        SC = [dict(x=short_close_time[i],title='SC',text = 'SC,price:{}'.format(short_close['price'][i]))\
              for i in range(0,len(short_close_time))]

        H.add_data_set(LO,'flags',style = dict(fontSize = '0.6em'),shape = 'circlepin',onSeries = 'dataseries')
        H.add_data_set(LC,'flags',style = dict(fontSize = '0.6em'),shape = 'circlepin',onSeries = 'dataseries')
        H.add_data_set(SO,'flags',style = dict(fontSize = '0.6em'),shape = 'circlepin',onSeries = 'dataseries')
        H.add_data_set(SC,'flags',style = dict(fontSize = '0.6em'),shape = 'circlepin',onSeries = 'dataseries')

        prices_adj = MeanReversion.contain_treat(prices)
        prices_part = MeanReversion.part_old(prices_adj)
        
#         四种分型分别作图，不好看
#         first_top = prices_part[prices_part['parting'] == 1]
#         first_top_list = first_top[['DATETIME','open']].values.tolist()
#         first_bottom = prices_part[prices_part['parting'] == -1]
#         first_bottom_list = first_bottom[['DATETIME','open']].values.tolist()
#         second_top = prices_part[prices_part['parting'] == 2]
#         second_top_list = second_top[['DATETIME','open']].values.tolist()
#         second_bottom = prices_part[prices_part['parting'] == -2]
#         second_bottom_list = second_bottom[['DATETIME','open']].values.tolist()
        
#         H.add_data_set(first_top_list,'line','1top',lineWidth = 1)
#         H.add_data_set(first_bottom_list,'line','1bottom',lineWidth = 1,)
#         H.add_data_set(second_top_list,'line','2top',lineWidth = 1)
#         H.add_data_set(second_bottom_list,'line','2bottom',lineWidth = 1)
        parting = prices_part[prices_part['parting'] != 0]
        parting_list = parting[['DATETIME','open']].values.tolist()
        pen_point = prices_part[prices_part['pen_point'] != 0]
        pen_point_list = pen_point[['DATETIME','open']].values.tolist()
        
        H.add_data_set(parting_list,'line','parting',lineWidth = 2)
        H.add_data_set(pen_point_list,'line','pen_point',lineWidth = 2)
        return H
    
    
    def FigTradesSig_update_prices(code:str,start:str,end:str,trades_df,logs_df
                                   ,prices,title = '第三买卖点策略'):
        '''
        在K线图的基础上标记开平仓交易记录,区分开平仓和止损平仓
        '''
        class ContFutureSymbolFilter(D.FutContContractFilter):
            @staticmethod
            def future_suffix_replace(symbol_str: str):
                return symbol_str if '.CFE' not in symbol_str[0] else [symbol_str[0].replace(".CFE", ".CF")]

            def symbols_during(self, start_dt: str, end_dt: str):
                main_contracts_df = self._query_main_contract(symbols=self.symbols, start=start_dt, end=end_dt)
                if not main_contracts_df.empty:
                    cont_list = []
                    for i in range(len(main_contracts_df)):
                        sub_cont = (main_contracts_df.iloc[i].symbol, main_contracts_df.iloc[i].start,
                                    main_contracts_df.iloc[i].end, self.future_suffix_replace([main_contracts_df.iloc[i].mapping_symbol]))
                        cont_list.append(sub_cont)
                return cont_list
        
#         prices = D.query_tsdata(datasource='future_kline_1min', symbols=ContFutureSymbolFilter(code), fields='*', start=start, end=end)
#         prices_list = []
#         for df in prices:
# #             #xhq modify
# #             df.index = pd.Series(df.index).shift(-1)
# #             df = df.iloc[:-1,:]
# #             ###
#             prices_list.append(df)
#         prices_df = pd.concat(prices_list)

        
#         prices = prices_df[['Symbol', 'open', 'high', 'low', 'close']]
#         prices.reset_index(inplace=True)
#         prices = prices.rename(columns={'index':'DATETIME', 'Symbol': 'code'})
        H = Highstock(offline=True)
        def add_offline_mode(H):
            highstock_css = ["http://orientlab.orientsec.com.cn:30080/static/highcharts/highslide.css"]
            highstock_js = ["http://orientlab.orientsec.com.cn:30080/static/highcharts/jquery.min.js",
                            "http://orientlab.orientsec.com.cn:30080/static/highcharts/highstock.js",
                            "http://orientlab.orientsec.com.cn:30080/static/highcharts/exporting.js",
                            "http://orientlab.orientsec.com.cn:30080/static/highcharts/highcharts-more.js",
                        ]
            H.JSsource.clear()
            H.CSSsource.clear()
            H.add_CSSsource(highstock_css)
            H.add_JSsource(highstock_js)
            return H
        H = add_offline_mode(H)
        
        prices_list = prices[['DATETIME', 'open', 'high', 'low', 'close']].values.tolist()
        H.add_data_set(prices_list, 'candlestick', '{} Prices'.format(code), id = 'dataseries')
        
        title = title
        width = '200px'
        valueDecimals = 4
        
        options = {
                    'rangeSelector': {
                        'selected': 0
                    },

                    'title': {
                        'text': title
                    },
                    'tooltip': {
                        'style': {
                            'width': width
                        },
                        'valueDecimals': valueDecimals,
                        'shared': True
                    },
                    'yAxis': {
                        'title': {
                            'text': '价格'
                        }
                    },
                    'legend':{
                        'enabled':True,
                        'align':'center',
                    },
                    'plotOptions': {
                        'candlestick': {
                            'color': 'green',
                            'upColor': 'red',
                        }
                    },
                }
        H.set_dict_options(options)
        
        trades_df['datetime'] = trades_df.index.strftime("%Y-%m-%d %H:%M:%S")     #统一时间格式
        trades_df['datetime'] = pd.to_datetime(trades_df['datetime'])
        long_open = trades_df[(trades_df['open_close'] == 'OPEN')&(trades_df['LS'] == 'LONG')]
#         long_close = trades_df[(trades_df['open_close'] == 'CLOSE')&(trades_df['LS'] == 'LONG')]
        short_open = trades_df[(trades_df['open_close'] == 'OPEN')&(trades_df['LS'] == 'SHORT')]
#         short_close = trades_df[(trades_df['open_close'] == 'CLOSE')&(trades_df['LS'] == 'SHORT')]
        long_open_time = long_open.datetime.tolist()
#         long_close_time = long_close.datetime.tolist()
        short_open_time = short_open.datetime.tolist()
#         short_close_time = short_close.datetime.tolist()
        
    

        logs_df = pd.DataFrame(logs_df).copy()
        logs_df.reset_index(inplace = True)
        logs_df.rename({'0':'datetime','1':'log'},axis = 1,inplace = True)
        logs_df.rename({0:'datetime',1:'log'},axis = 1,inplace = True)
        logs_df['datetime'] = logs_df['datetime'].apply(lambda x:x.strftime("%Y-%m-%d %H:%M:%S"))     #统一时间格式
        logs_df['datetime'] = pd.to_datetime(logs_df['datetime'])
        logs_df['logs_shorter'] = logs_df['log'].apply(lambda x:x[:-7])

        
        stop_lc = logs_df[logs_df['logs_shorter'] == '破底CL']
        stop_sc = logs_df[logs_df['logs_shorter'] == '破顶CS']
        normal_lc = logs_df[logs_df['logs_shorter'] == 'CL']
        normal_sc = logs_df[logs_df['logs_shorter'] == 'CS']
        end_lc = logs_df[logs_df['logs_shorter'] == 'end_CL']
        end_sc = logs_df[logs_df['logs_shorter'] == 'end_CS']

        stop_lc_time = stop_lc.datetime.to_list()
        stop_sc_time = stop_sc.datetime.to_list()
        normal_lc_time = normal_lc.datetime.to_list()
        normal_sc_time = normal_sc.datetime.to_list()
        end_lc_time = end_lc.datetime.to_list()
        end_sc_time = end_sc.datetime.to_list()
        
        #标识位置
        LO = [dict(x=long_open_time[i],title='LO',text = 'LO,price:{}'.format(long_open['price'][i])) \
            for i in range(0,len(long_open_time))]
        SO = [dict(x=short_open_time[i],title='SO',text = 'SO,price:{}'.format(short_open['price'][i]))\
            for i in range(0,len(short_open_time))]
        
        NLC = [dict(x=normal_lc_time[i],title='NLC',text = 'NLC,price:{}'.format(normal_lc['log'].iloc[i][-6:]))\
            for i in range(0,len(normal_lc_time))]
        NSC = [dict(x=normal_sc_time[i],title='NSC',text = 'NSC,price:{}'.format(normal_sc['log'].iloc[i][-6:]))\
            for i in range(0,len(normal_sc_time))]
        SLC = [dict(x=stop_lc_time[i],title='SLC',text = 'SLC,price:{}'.format(stop_lc['log'].iloc[i][-6:]))\
            for i in range(0,len(stop_lc_time))]
        SSC = [dict(x=stop_sc_time[i],title='SSC',text = 'SSC,price:{}'.format(stop_sc['log'].iloc[i][-6:]))\
            for i in range(0,len(stop_sc_time))]
        ELC = [dict(x=end_lc_time[i],title='ELC',text = 'ELC,price:{}'.format(end_lc['log'].iloc[i][-6:]))\
            for i in range(0,len(end_lc_time))]
        ESC = [dict(x=end_sc_time[i],title='ESC',text = 'ESC,price:{}'.format(end_sc['log'].iloc[i][-6:]))\
            for i in range(0,len(end_sc_time))]

        #标识形状
        H.add_data_set(LO,'flags',style = dict(fontSize = '0.6em'),shape = 'circlepin',onSeries = 'dataseries',name = 'LO')
        H.add_data_set(SO,'flags',style = dict(fontSize = '0.6em'),shape = 'circlepin',onSeries = 'dataseries',name = 'SO')
        
        H.add_data_set(NLC,'flags',style = dict(fontSize = '0.6em'),shape = 'squarepin',onSeries = 'dataseries',name = 'NLC')
        H.add_data_set(NSC,'flags',style = dict(fontSize = '0.6em'),shape = 'squarepin',onSeries = 'dataseries',name = 'NSC')
        H.add_data_set(SLC,'flags',style = dict(fontSize = '0.6em'),shape = 'squarepin',onSeries = 'dataseries',name = 'SLC')
        H.add_data_set(SSC,'flags',style = dict(fontSize = '0.6em'),shape = 'squarepin',onSeries = 'dataseries',name = 'SSC')
        H.add_data_set(ELC,'flags',style = dict(fontSize = '0.6em'),shape = 'squarepin',onSeries = 'dataseries',name = 'ELC')
        H.add_data_set(ESC,'flags',style = dict(fontSize = '0.6em'),shape = 'squarepin',onSeries = 'dataseries',name = 'ESC')

        return H