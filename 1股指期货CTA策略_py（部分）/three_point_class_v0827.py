import os 
os.chdir('/home/jovyan/xhq/main/parting/')
import numpy as np
import pandas as pd


from algoqi.data import D, plotutils
D.switch_zxzx_client(access_key='e7e2de63f95674632824ed6b2be8dd1f', secret_key='d43ca617fe7048e4ccfb158dde8e1c32')
D.load()


from highcharts import Highstock
from backtest_class import backtest,roll_test
from ResAssese import ResultAssese
import datetime
from interval_theory import K_cut

# #第三买卖点修改前
# from market_timing_lab import MeanReversion
#第三买卖点修改后，在笔完成时才出现信号
from market_timing_lab_v0827 import MeanReversion
from DataRelated import DataProcess

class three_point:
    
#     def __init__(self,version = 'v0827'):
#         if version == 'v0827':
#             from market_timing_lab_v0827 import MeanReversion
#         else:
#             from market_timing_lab import MeanReversion
            
        
    def three_init(raw_prices,raw_time):
        '''
        example:
        ---------
        for raw_time in raw_prices['DATETIME'][1:]:
            pivot_latest,trading_point_level_3 = three_point.three_init(raw_prices,raw_time)

        function:
        --------
        从头开始算
        返回最近的中枢和第三买卖点
        '''

        prices = raw_prices.loc[raw_prices['DATETIME'] < raw_time,:]
        prices_latest = raw_prices.loc[raw_prices['DATETIME'] == raw_time,:]

        prices_adj = MeanReversion.contain_treat(prices)
        prices_part = MeanReversion.part_old(prices_adj)
        pen_point = MeanReversion.pen_point_prices(prices_part)

    #     for pl_i in range(len(prices_latest)-1):
    #         prices_adj_latest = MeanReversion.contain_treat_latest(prices_adj, prices_latest.iloc[pl_i:pl_i+1, :])
    #         prices_adj =prices_adj_latest
        prices_adj_latest = MeanReversion.contain_treat_latest(prices_adj, prices_latest)
        prices_adj_latest = prices_adj_latest[prices_adj_latest['DATETIME'] > prices_part['DATETIME'].iloc[-1]].drop_duplicates(subset=['DATETIME'])


    #     for adj_i in range(len(prices_adj_latest)-1):
    #         prices_part_latest = MeanReversion.part_old_latest(prices_part, prices_adj_latest.iloc[adj_i:adj_i+1, :])
    #         prices_part = prices_part_latest
        prices_part_latest = MeanReversion.part_old_latest(prices_part, prices_contained_latest=prices_adj_latest)
        pen_point_latest = MeanReversion.pen_point_prices(prices_part_latest)


        pivot_latest = {'DATETIME': None, 'pivot_time': None, 'pivot_start': None, 'last_pivot_end':None,
        'processed_time': None, 'zg': None, 'zd': None, 'gg': None, 'dd': None, 'direction': None}

        for pen_i in pen_point['DATETIME'].to_list():
            trend_prices = pen_point.loc[pen_point['DATETIME']<=pen_i, :]
            pivot_latest = MeanReversion.pivot_latest(pivot_latest, trend_prices)

        trend_low_level_latest = pen_point_latest.iloc[-1:, :]
        trend_low_level_last = pen_point_latest.iloc[:-1,:]
        trading_point_last = {}

        trading_point_level_3 = MeanReversion.trading_point_level_3(pivot_latest, trend_low_level_latest,
            trend_low_level_last, trading_point_last)

    #     print(pen_i)
    #     print('pivot_latest\n',pivot_latest)
    #     print('trading_point_level_3\n',trading_point_level_3)
    #     print('*******'*5)

        return pivot_latest,trading_point_level_3
    
    def three_point_init(prices_init):
        '''
        

        example:
        ---------
        for raw_time in raw_prices['DATETIME'][1:]:
            pivot_latest,trading_point_level_3 = three_point.three_init(raw_prices,raw_time)

        function:
        --------
        算出初始化数据，第一行
        '''

        prices_adj = MeanReversion.contain_treat(prices_init)
        prices_part = MeanReversion.part_old(prices_adj)
        pen_point = MeanReversion.pen_point_prices(prices_part)

        pivot_latest = {'DATETIME': None, 'pivot_time': None, 'pivot_start': None, 'last_pivot_end':None,
        'processed_time': None, 'zg': None, 'zd': None, 'gg': None, 'dd': None, 'direction': None}

        for pen_i in pen_point['DATETIME'].to_list():
            trend_prices = pen_point.loc[pen_point['DATETIME']<=pen_i, :]
            pivot_latest = MeanReversion.pivot_latest(pivot_latest, trend_prices)

        trend_low_level_latest = pen_point.iloc[-1:, :]
        trend_low_level_last = pen_point.iloc[:-1,:]

        trading_point_last = {}

        trading_point_level_3 = MeanReversion.trading_point_level_3(pivot_latest, trend_low_level_latest,
                                                                    trend_low_level_last, trading_point_last)


        return prices_adj,prices_part,pivot_latest,trading_point_level_3
    
    def three_point_latest(prices_latest,prices_adj,prices_part,pivot_latest,trading_point_level_3):
        '''
        prices_latest一次传入一行
        
        example:
        ---------
        prices_init = raw_prices.iloc[:1,:]
        prices_adj,prices_part,pivot_latest,trading_point_level_3 = three_point_init(prices_init)
        for raw_time in raw_prices['DATETIME'].iloc[1:]:
            prices_latest = raw_prices.loc[raw_prices['DATETIME'] == raw_time,:]
            prices_adj,prices_part,pivot_latest,trading_point_level_3 = three_point_latest(prices_latest,prices_adj,prices_part,pivot_latest,trading_point_level_3)
            if (raw_time >= pd.Timestamp('2019-09-23 13:13:00')) and (raw_time <= pd.Timestamp('2019-09-23 13:17:00')):
                print(raw_time)
                print('pivot_latest\n',pivot_latest)
                print('trading_point_level_3\n',trading_point_level_3)
        '''

        prices_adj = MeanReversion.contain_treat_latest(prices_adj, prices_latest)
        prices_adj_latest = prices_adj[prices_adj['DATETIME'] > prices_part['DATETIME'].iloc[-1]].drop_duplicates(subset=['DATETIME'])
    #     prices_adj_latest = prices_adj.iloc[-1:,:]

        #prices_part_latest:prices_part; pen_point_latest:pen_point
        prices_part = MeanReversion.part_old_latest(prices_part, prices_contained_latest=prices_adj_latest)
        pen_point = MeanReversion.pen_point_prices(prices_part)


        pivot_latest = MeanReversion.pivot_latest(pivot_latest, trend_prices = pen_point)
        trend_low_level_latest = pen_point.iloc[-1:, :]
        trend_low_level_last = pen_point.iloc[:-1,:]

        trading_point_last = trading_point_level_3

        trading_point_level_3 = MeanReversion.trading_point_level_3(pivot_latest, trend_low_level_latest,
                                                                    trend_low_level_last, trading_point_last)

        return prices_adj,prices_part,pivot_latest,trading_point_level_3
  

    def three_point_init_level2(prices_init,prices_init_high_level):
        '''
        高级K线算中枢，低级K线算买卖点
        一次计算整个dataframe的trading_point_level_3
        '''
        def pen_point(prices_init):
            prices_adj = MeanReversion.contain_treat(prices_init)
            prices_part = MeanReversion.part_old(prices_adj)
            pen_point = MeanReversion.pen_point_prices(prices_part)
            return prices_adj,prices_part,pen_point

        pivot_latest = {'DATETIME': None, 'pivot_time': None, 'pivot_start': None, 'last_pivot_end':None,
        'processed_time': None, 'zg': None, 'zd': None, 'gg': None, 'dd': None, 'direction': None}


        prices_adj_high_level,prices_part_high_level,pen_point_high_level = pen_point(prices_init_high_level)
        for pen_i in pen_point_high_level['DATETIME'].to_list():
            trend_prices = pen_point_high_level.loc[pen_point_high_level['DATETIME']<=pen_i, :]
            pivot_latest = MeanReversion.pivot_latest(pivot_latest, trend_prices)

        prices_adj,prices_part,pen_point = pen_point(prices_init)
        trend_low_level_latest = pen_point.iloc[-1:, :]
        trend_low_level_last = pen_point.iloc[:-1,:]

        trading_point_last = {}

        trading_point_level_3 = MeanReversion.trading_point_level_3(pivot_latest, trend_low_level_latest,
                                                                    trend_low_level_last, trading_point_last)


        return prices_adj,prices_part,prices_adj_high_level,prices_part_high_level,pivot_latest,trading_point_level_3
    

    def three_point_latest_level2(prices_latest,prices_latest_high_level,prices_adj,prices_part,\
                                  prices_adj_high_level,prices_part_high_level,pivot_latest,trading_point_level_3):
        '''
        高级K线算中枢，低级K线算买卖点
        prices_latest一次传入一行
        example
        ---------
        prices_init = raw_prices.iloc[:1,:]
        prices_init_high_level = raw_prices_high_level.iloc[:1,:]
        prices_adj,prices_part,prices_adj_high_level,prices_part_high_level,pivot_latest,trading_point_level_3 = \
                                                        three_point.three_point_init_level2(prices_init,prices_init_high_level)
        for raw_time in raw_prices['DATETIME'].iloc[1:]:
            prices_latest = raw_prices.loc[raw_prices['DATETIME'] == raw_time,:]
            prices_latest_high_level = raw_prices_high_level.loc[raw_prices_high_level['DATETIME'] == raw_time,:]

            prices_adj,prices_part,prices_adj_high_level,prices_part_high_level,pivot_latest,trading_point_level_3 =\
                                    three_point.three_point_latest_level2(prices_latest,prices_latest_high_level,prices_adj,prices_part,\
                                      prices_adj_high_level,prices_part_high_level,pivot_latest,trading_point_level_3)
            print(raw_time)
        #     print('prices_part\n',prices_part)
            print('pivot_latest\n',pivot_latest)
            print('trading_point_level_3\n',trading_point_level_3)
        '''
        def pen_point_latest(prices_latest,prices_adj,prices_part):
            prices_adj = MeanReversion.contain_treat_latest(prices_adj, prices_latest)
#             prices_adj_latest = prices_adj[prices_adj['DATETIME'] > prices_part['DATETIME'].iloc[-1]].drop_duplicates(subset=['DATETIME'])
            prices_adj_latest = prices_adj.iloc[-1:,:]

            #prices_part_latest:prices_part; pen_point_latest:pen_point
            prices_part = MeanReversion.part_old_latest(prices_part,
                                                        prices_contained_latest=prices_adj_latest)
            pen_point = MeanReversion.pen_point_prices(prices_part)
            return prices_adj,prices_part,pen_point
        
        if len(prices_latest_high_level) != 0:
            prices_adj_high_level,prices_part_high_level,pen_point_high_level = pen_point_latest(prices_latest_high_level,
                                                                                                 prices_adj_high_level,
                                                                                                 prices_part_high_level)
            pivot_latest = MeanReversion.pivot_latest(pivot_latest, trend_prices = pen_point_high_level)
            
#             print('prices_latest_high_level\n',prices_latest_high_level)
#             print('pivot_latest\n',pivot_latest)
 
        if len(prices_latest) != 0:
            prices_adj,prices_part,pen_point = pen_point_latest(prices_latest,prices_adj,prices_part)
            trend_low_level_latest = pen_point.iloc[-1:, :]
            trend_low_level_last = pen_point.iloc[:-1,:]

            trading_point_last = trading_point_level_3
#             print('\ntrend_low_level_latest\n',trend_low_level_latest)
#             print('\npivot_latest\n',pivot_latest)
#             print('Running')
            trading_point_level_3 = MeanReversion.trading_point_level_3(pivot_latest, trend_low_level_latest,
                                                                        trend_low_level_last, trading_point_last)
        else:
            pass
#             print('\n{}之后一根低级K线数据缺失，trading_point_level_3延用上一时间戳结论。'
#                   .format(prices_adj['DATETIME'].iloc[-1]))


        return prices_adj,prices_part,prices_adj_high_level,prices_part_high_level,pivot_latest,trading_point_level_3


    ##v0827:改成先计算三买,再计算中枢!!!    
    def three_point_latest_level2_v0827(prices_latest,prices_latest_high_level,prices_adj,prices_part,\
                                  prices_adj_high_level,prices_part_high_level,pivot_latest,trading_point_level_3):
        '''
        高级K线算中枢，低级K线算买卖点
        prices_latest一次传入一行
        example
        ---------
        prices_init = raw_prices.iloc[:1,:]
        prices_init_high_level = raw_prices_high_level.iloc[:1,:]
        prices_adj,prices_part,prices_adj_high_level,prices_part_high_level,pivot_latest,trading_point_level_3 = \
                                                        three_point.three_point_init_level2(prices_init,prices_init_high_level)
        for raw_time in raw_prices['DATETIME'].iloc[1:]:
            prices_latest = raw_prices.loc[raw_prices['DATETIME'] == raw_time,:]
            prices_latest_high_level = raw_prices_high_level.loc[raw_prices_high_level['DATETIME'] == raw_time,:]

            prices_adj,prices_part,prices_adj_high_level,prices_part_high_level,pivot_latest,trading_point_level_3 =\
                                    three_point.three_point_latest_level2(prices_latest,prices_latest_high_level,prices_adj,prices_part,\
                                      prices_adj_high_level,prices_part_high_level,pivot_latest,trading_point_level_3)
            print(raw_time)
        #     print('prices_part\n',prices_part)
            print('pivot_latest\n',pivot_latest)
            print('trading_point_level_3\n',trading_point_level_3)
        '''
        def pen_point_latest(prices_latest,prices_adj,prices_part):
            prices_adj = MeanReversion.contain_treat_latest(prices_adj, prices_latest)
#             prices_adj_latest = prices_adj[prices_adj['DATETIME'] > prices_part['DATETIME'].iloc[-1]].drop_duplicates(subset=['DATETIME'])
            prices_adj_latest = prices_adj.iloc[-1:,:]

            #prices_part_latest:prices_part; pen_point_latest:pen_point
            prices_part = MeanReversion.part_old_latest(prices_part,
                                                        prices_contained_latest=prices_adj_latest)
            pen_point = MeanReversion.pen_point_prices(prices_part)
            return prices_adj,prices_part,pen_point
        

        
 
        if len(prices_latest) != 0:
            prices_adj,prices_part,pen_point = pen_point_latest(prices_latest,prices_adj,prices_part)
            trend_low_level_latest = pen_point.iloc[-1:, :]
            trend_low_level_last = pen_point.iloc[:-1,:]

            trading_point_last = trading_point_level_3
#             print('\ntrend_low_level_latest\n',trend_low_level_latest)
#             print('\npivot_latest\n',pivot_latest)
#             print('Running')
            trading_point_level_3 = MeanReversion.trading_point_level_3(pivot_latest, trend_low_level_latest,
                                                                        trend_low_level_last, trading_point_last)
        else:
            pass
#             print('\n{}之后一根低级K线数据缺失，trading_point_level_3延用上一时间戳结论。'
#                   .format(prices_adj['DATETIME'].iloc[-1]))

        if len(prices_latest_high_level) != 0:
            prices_adj_high_level,prices_part_high_level,pen_point_high_level = pen_point_latest(prices_latest_high_level,
                                                                                                 prices_adj_high_level,
                                                                                                 prices_part_high_level)
            pivot_latest = MeanReversion.pivot_latest(pivot_latest, trend_prices = pen_point_high_level)
            
#             print('prices_latest_high_level\n',prices_latest_high_level)
#             print('pivot_latest\n',pivot_latest)



        return prices_adj,prices_part,prices_adj_high_level,prices_part_high_level,pivot_latest,trading_point_level_3


#     def three_point_all(prices_high_level,prices_low_level):
#         '''
#         使用过去所有数据计算第三买卖点
#         '''
#         #### 2.1形成高级k线的中枢

#         prices_con_high_level = MeanReversion.contain_treat(prices_high_level, date_col='DATETIME', keep='last', col_move=None)

#         part_high_level = MeanReversion.part_old(prices_con_high_level)

#         trend_prices_high_level = MeanReversion.pen_point_prices(part_high_level,False) # 默认是False

#         pivot_high_level = MeanReversion.pivot_all(trend_prices_high_level, trend_col='pen_point', accessible_time_col='pen_point_time')

#         #### 2.2形成低级k线的笔

#         prices_con_low_level = MeanReversion.contain_treat(prices_low_level, date_col='DATETIME', keep='last', col_move=None)

#         part_low_level = MeanReversion.part_old(prices_con_low_level)

#         trend_prices_low_level = MeanReversion.pen_point_prices(part_low_level,False) # 默认是False

#         ####  2.3 高级中枢+ 低级笔 = 三买

#         trading_point = MeanReversion.trading_point_all_level_3(pivot_high_level, trend_prices_low_level)
        
#         return pivot_high_level,trading_point
    


    def three_point_all(prices_high_level,prices_low_level):
        '''
        使用过去所有数据计算第三买卖点
        '''
        try:
            #### 2.1形成高级k线的中枢

            prices_con_high_level = MeanReversion.contain_treat(prices_high_level, date_col='DATETIME', keep='last', col_move=None)

            part_high_level = MeanReversion.part_old(prices_con_high_level)
        #     print(part_high_level)

            trend_prices_high_level = MeanReversion.pen_point_prices(part_high_level,False) # 默认是False
        #     print(trend_prices_high_level)

            pivot_high_level = MeanReversion.pivot_all(trend_prices_high_level, trend_col='pen_point', accessible_time_col='pen_point_time')

            #### 2.2形成低级k线的笔

            prices_con_low_level = MeanReversion.contain_treat(prices_low_level, date_col='DATETIME', keep='last', col_move=None)

            part_low_level = MeanReversion.part_old(prices_con_low_level)

            trend_prices_low_level = MeanReversion.pen_point_prices(part_low_level,False) # 默认是False

            ####  2.3 高级中枢+ 低级笔 = 三买

            trading_point = MeanReversion.trading_point_all_level_3(pivot_high_level, trend_prices_low_level)

        except Exception as e:
            pivot_latest = {'DATETIME': None, 'pivot_time': None, 'pivot_start': None,
              'last_pivot_end': None, 'processed_time': None, 'zg': None, 
              'zd': None, 'gg': None, 'dd': None, 'direction': None}
            trading_point_level_3 = {}
            return pivot_latest,trading_point_level_3
        else:
            pivot_latest =pivot_high_level.iloc[-1,:].to_dict()
            trading_point_level_3 = trading_point.iloc[-1,:].to_dict()
            return pivot_latest,trading_point_level_3
    




    def latest_draw(py_path0 ,
                    save_name0,
                     start = '20190102',
                     end = '20191231',
                      code = "IC00.CFE"
                     ):
        ## 3 第三买卖点绘图_latest
        #### 一、导入包和数据
        #回测交易数据
        # logs_df0 = pd.read_csv('./circle/logs_'+save_name0+start+'_'+end+'.csv')
        # trades_df0 = pd.read_csv('./circle/trades_'+save_name0+start+'_'+end+'.csv')
        # trades_df0,logs_df0 = roll_test.init_handle(trades_df0,logs_df0)
        trades_df0 = pd.read_pickle('./第三买卖点/strategy_save/trades_'+save_name0+start+'_'+end+'.pkl')
        logs_df0 = pd.read_pickle('./第三买卖点/strategy_save/logs_'+save_name0+start+'_'+end+'.pkl')

        #高级K线数据:中枢
        part_high_level0 = pd.read_pickle(f'./第三买卖点/strategy_save/prices_part_high_level_{save_name0}_{start}_{end}.pkl' )
        pivot_high_level0 = pd.read_pickle(f'./第三买卖点/strategy_save/pivot_df_{save_name0}_{start}_{end}.pkl' )

        #低级K线数据:笔
        part_low_level0 = pd.read_pickle(f'./第三买卖点/strategy_save/prices_part_{save_name0}_{start}_{end}.pkl' )
        trend_prices_low_level0 =  MeanReversion.pen_point_prices(part_low_level0,False) # 默认是False

        #三买数据
        trading_point0 = pd.read_pickle(f'./第三买卖点/strategy_save/three_point_df_{save_name0}_{start}_{end}.pkl' )

        # #取部分K线数据数据绘图
        prices_low_level0 = pd.read_pickle('./第三买卖点/1minK_20190102_20191231.pkl')

        ##取部分数据
        prices_low_level = prices_low_level0.copy()
        end1 = (pd.Timestamp(end) + datetime.timedelta(days=1)).strftime('%Y%m%d')
        prices_low_level = prices_low_level0[(prices_low_level0['DATETIME'] <= end1)&
                                            (prices_low_level0['DATETIME'] >= start)].copy()

        # # 保存计算数据
        # part_low_level0.to_pickle(f'./第三买卖点/vs/{save_name0}_part_low_level0_{start}_{end}.pkl')
        # pivot_high_level0.to_pickle(f'./第三买卖点/vs/{save_name0}_pivot_high_level0_{start}_{end}.pkl')
        # trading_point0.to_pickle(f'./第三买卖点/vs/{save_name0}_trading_point0_{start}_{end}.pkl')

        #### 二，价格合并，形成顶底分型、笔、走势中枢

        #### 2.1形成高级k线的中枢

#         pivot_high_level = pivot_high_level0.dropna(subset = ['zd','zg'],how = 'all').drop_duplicates(subset = pivot_high_level0.columns).copy()
#         pivot_high_level = pivot_high_level.reset_index(drop = True)
        pivot = pivot_high_level0.copy()
        
        pivot_fill = pivot.fillna(method='backfill')
        filter_index = [i for i in pivot_fill.index if (pivot_fill.loc[i, 'last_pivot_end'] is None or
                                                        pivot_fill.loc[i, 'DATETIME'] <= pivot_fill.loc[
                                                            i, 'last_pivot_end'])]
        pivot_fill = pivot_fill.reindex(filter_index)
        pivot_fill = pivot_fill.rename(columns={'last_pivot_end': 'pivot_end'})
        pivot_fill.reset_index(drop=True, inplace=True)
        pivot_high_level = pivot_fill.copy()

        # pivot_high_level = pivot_high_level0.dropna(subset = ['zd','zg'],how = 'all')
        # pivot_high_level = pivot_high_level.reset_index(drop = True)


        #### 2.2形成低级k线的笔

        trend_prices_low_level = trend_prices_low_level0.copy()

        ####  2.3 高级中枢+ 低级笔 = 三买

        trading_point  = trading_point0.drop_duplicates(subset = ['DATETIME']).copy()
        trading_point = trading_point[(trading_point['trading_point'] == 3 )|\
                                            (trading_point['trading_point'] == -3)]

        #### 三、画图:低级K线

        p_start = start
        p_end = end
        prices = prices_low_level

        H = ResultAssese.FigTradesSig_update_prices(code,p_start,p_end,trades_df0,logs_df0,prices)

        # H = ResultAssese.FigTradesSig_update_prices(code,p_start,p_end,trades_df0,logs_df0,prices_low_level)

        # H.set_dict_options(options)

        #### 四、绘图：高级中枢、低级笔、交易点

        #低级K线trend（笔）
        trend_prices_low_level_list = trend_prices_low_level[['DATETIME','prices']].values.tolist()
        H.add_data_set(trend_prices_low_level_list, 'line', name = 'trend_prices_low_level', id='trend_prices_low_level')

        pivot_high_level_list = pivot_high_level[['DATETIME', 'zg', 'zd']].values.tolist()
        H.add_data_set(pivot_high_level_list, 'arearange', name = 'pivot_high_level')

        trading_point = trading_point
        trading_point_long = trading_point[trading_point['trading_point'] == 3]
        trading_point_short = trading_point[trading_point['trading_point'] == -3]

        trading_point_time = trading_point_long.DATETIME.tolist()
        trading_point_level_3_dict = [dict(x=trading_point_time[i], text = 'trading_point_3',title = 'L3') for i in range(0,len(trading_point_time))]

        H.add_data_set(trading_point_level_3_dict,'flags',style = dict(fontSize = '0.6em'), shape = 'circlepin',name = 'trading_point_L3')
        #, onSeries = 'trend_prices_low_level'

        trading_point_time = trading_point_short.DATETIME.tolist()
        trading_point_level_3_dict = [dict(x=trading_point_time[i], text = 'trading_point_3',title = 'S3') for i in range(0,len(trading_point_time))]

        H.add_data_set(trading_point_level_3_dict,'flags',style = dict(fontSize = '0.6em'), shape = 'squarepin',name = 'trading_point_S3')
        #, onSeries = 'trend_prices_low_level'

        #pivot drop columns
        return H
    
    def strategy_draw(param):
        '''
        在三买计算version0827中，该中枢绘制方式应该被弃用。
        '''
        code = param['code']
        start = param['start']
        end = param['end']
        py_path0 = param['py_path0']
        save_name0 = param['save_name0']
        k_min_high_level = param['k_min_high_level']
        k_min_low_level = param['k_min_low_level']
        prices_start = param['prices_start']
        prices_end = param['prices_end']
        end1 = (pd.Timestamp(end) + datetime.timedelta(days=1)).strftime('%Y%m%d')

        #回测交易数据
        # logs_df0 = pd.read_csv('./circle/logs_'+save_name0+start+'_'+end+'.csv')
        # trades_df0 = pd.read_csv('./circle/trades_'+save_name0+start+'_'+end+'.csv')
        # trades_df0,logs_df0 = roll_test.init_handle(trades_df0,logs_df0)
        trades_df0 = pd.read_pickle('./第三买卖点/strategy_save/trades_'+save_name0+start+'_'+end+'.pkl')
        logs_df0 = pd.read_pickle('./第三买卖点/strategy_save/logs_'+save_name0+start+'_'+end+'.pkl')

        #高级K线数据:中枢
        part_high_level0 = pd.read_pickle(f'./第三买卖点/strategy_save/prices_part_high_level_{save_name0}_{start}_{end}.pkl' )
        pivot_high_level0 = pd.read_pickle(f'./第三买卖点/strategy_save/pivot_df_{save_name0}_{start}_{end}.pkl' )

        #低级K线数据:笔
        part_low_level0 = pd.read_pickle(f'./第三买卖点/strategy_save/prices_part_{save_name0}_{start}_{end}.pkl' )
        trend_prices_low_level0 =  MeanReversion.pen_point_prices(part_low_level0,False) # 默认是False

        #三买数据
        trading_point0 = pd.read_pickle(f'./第三买卖点/strategy_save/three_point_df_{save_name0}_{start}_{end}.pkl' )

        # #取部分K线数据数据绘图
        prices_low_level0 = pd.read_pickle(f'./第三买卖点/{k_min_low_level}minK_{prices_start}_{prices_end}.pkl')

        ##取部分数据
        prices_low_level = prices_low_level0.copy()

        prices_low_level = prices_low_level0[(prices_low_level0['DATETIME'] <= end1)&
                                            (prices_low_level0['DATETIME'] >= start)].copy()

        # # 保存计算数据
        # part_low_level0.to_pickle(f'./第三买卖点/vs/{save_name0}_part_low_level0_{start}_{end}.pkl')
        # pivot_high_level0.to_pickle(f'./第三买卖点/vs/{save_name0}_pivot_high_level0_{start}_{end}.pkl')
        # trading_point0.to_pickle(f'./第三买卖点/vs/{save_name0}_trading_point0_{start}_{end}.pkl')

        #### 二，价格合并，形成顶底分型、笔、走势中枢

        #### 2.1形成高级k线的中枢
        ##中枢绘图1：

        # pivot_high_level1 = pivot_high_level0.dropna(subset = ['zd','zg'],how = 'all').drop_duplicates(subset = pivot_high_level0.columns).copy()
        # pivot_high_level1 = pivot_high_level1.reset_index(drop = True)

        # pivot_high_level1

        # pivot_high_level = pivot_high_level0.dropna(subset = ['zd','zg'],how = 'all')
        # pivot_high_level = pivot_high_level.reset_index(drop = True)
        
        
        ##中枢绘图2：会缺失部分中枢 -> pivot_prices_sigle = pivot_all[pivot_all['DATETIME'] == pivot_all['pivot_end']]
#         pivot = pivot_high_level0.copy()

#         pivot_fill = pivot.fillna(method='backfill')
#         filter_index = [i for i in pivot_fill.index if (pivot_fill.loc[i, 'last_pivot_end'] is None or
#                                                         pivot_fill.loc[i, 'DATETIME'] <= pivot_fill.loc[
#                                                             i, 'last_pivot_end'])]
#         pivot_fill = pivot_fill.reindex(filter_index)
#         pivot_fill = pivot_fill.rename(columns={'last_pivot_end': 'pivot_end'})

#         pivot_fill.reset_index(drop=True, inplace=True)

#         #去重
#         pivot_fill = pivot_fill.drop_duplicates()

#         pivot_high_level1 = pivot_fill.copy()

#         def pivot_prices_new(pivot_all, prices):
#             """

#             Parameters
#             ----------
#             pivot_all
#             prices

#             Returns
#             -------

#             Examples
#             -------
#             >>> MeanReversion.pivot_prices_new(pivot, prices)

#             """
#             pivot_prices_sigle = pivot_all[pivot_all['DATETIME'] == pivot_all['pivot_end']]
#             pivot_prices = prices
#             pivot_prices['zd'] = np.nan
#             pivot_prices['zg'] = np.nan
#             pivot_prices.index = pivot_prices['DATETIME']
#             for i in pivot_prices_sigle.index:
#                 pivot_prices.loc[pivot_prices_sigle.loc[i, 'pivot_time']:pivot_prices_sigle.loc[i, 'pivot_end'], 'zd'] \
#                     = pivot_prices_sigle.loc[i, 'zd']
#                 pivot_prices.loc[pivot_prices_sigle.loc[i, 'pivot_time']:pivot_prices_sigle.loc[i, 'pivot_end'], 'zg'] \
#                     = pivot_prices_sigle.loc[i, 'zg']
#             pivot_prices = pivot_prices[['DATETIME', 'zd', 'zg']]
#             pivot_prices.reset_index(drop=True, inplace=True)
#             return pivot_prices

#         #非中枢位置为空
#         prices_high_level0 = pd.read_pickle(f'./第三买卖点/{k_min_high_level}minK_{prices_start}_{prices_end}.pkl')
#         pivot_high_level = pivot_prices_new(pivot_all = pivot_high_level1, prices = prices_high_level0)


        ##中枢绘图3：利用交易时间和zg、zd，不会出现缺失pivot，图中pivot起于确立时间，终止于消失时间。
        pivot_high_level1 = pivot_high_level0[['zd','zg']].copy()
        pivot_high_level1 = pivot_high_level1.dropna(subset = ['zd','zg'],how = 'all')
        pivot_high_level1['DATETIME'] = pivot_high_level1.index
        pivot_high_level1['DATETIME'] = pivot_high_level1['DATETIME'].apply(lambda x:pd.Timestamp(x))
        pivot_high_level1.reset_index(drop = True,inplace = True)

        def pivot_insert_nan(pivot_all,prices):
            '''
            pivot_all:处理过的pivot
            proces:高级Kline
            '''
            pivot_prices_sigle = pivot_all
            pivot_prices_sigle.index = pivot_all['DATETIME']
            pivot_prices = prices
            pivot_prices.index = pivot_prices['DATETIME']
            pivot_prices['zd'] = np.nan
            pivot_prices['zg'] = np.nan

            for i in pivot_prices_sigle['DATETIME']:
                pivot_prices.loc[i, 'zd'] \
                    = pivot_prices_sigle.loc[i, 'zd']
                pivot_prices.loc[i, 'zg'] \
                    = pivot_prices_sigle.loc[i, 'zg']
            pivot_prices = pivot_prices[[ 'zd', 'zg']]
            pivot_prices.sort_index(inplace = True)
        #     pivot_prices.drop('DATETIME',axis = 1,inplace = True)
            pivot_prices.reset_index(inplace = True)
            return pivot_prices

        prices_high_level0 = pd.read_pickle(f'./第三买卖点/{k_min_high_level}minK_20190102_20191231.pkl')
        prices_high_level1 = prices_high_level0[(prices_high_level0['DATETIME'] <= end1)&
                                            (prices_high_level0['DATETIME'] >= start)].copy()
        pivot_high_level = pivot_insert_nan(pivot_all = pivot_high_level1, prices = prices_high_level1)

        #### 2.2形成低级k线的笔

        trend_prices_low_level = trend_prices_low_level0.copy()

        ####  2.3 高级中枢+ 低级笔 = 三买

        trading_point  = trading_point0.drop_duplicates(subset = ['DATETIME']).copy()
        trading_point = trading_point[(trading_point['trading_point'] == 3 )|\
                                            (trading_point['trading_point'] == -3)]

        #### 三、画图:低级K线

        p_start = start
        p_end = end
        prices = prices_low_level

        H = ResultAssese.FigTradesSig_update_prices(code,p_start,p_end,trades_df0,logs_df0,prices)

        # H = ResultAssese.FigTradesSig_update_prices(code,p_start,p_end,trades_df0,logs_df0,prices_low_level)

        # H.set_dict_options(options)

        #### 四、绘图：高级中枢、低级笔、交易点

        #低级K线trend（笔）
        trend_prices_low_level_list = trend_prices_low_level[['DATETIME','prices']].values.tolist()
        H.add_data_set(trend_prices_low_level_list, 'line', name = 'trend_prices_low_level', id='trend_prices_low_level')

        pivot_high_level_list = pivot_high_level[['DATETIME', 'zg', 'zd']].values.tolist()
        H.add_data_set(pivot_high_level_list, 'arearange', name = 'pivot_high_level')

        trading_point = trading_point
        trading_point_long = trading_point[trading_point['trading_point'] == 3]
        trading_point_short = trading_point[trading_point['trading_point'] == -3]

        trading_point_time = trading_point_long.DATETIME.tolist()
#         #使用确立时间
#         trading_point_time = trading_point_long.trading_point_time.tolist()
        trading_point_level_3_dict = [dict(x=trading_point_time[i], text = 'trading_point_3',title = 'L3') for i in range(0,len(trading_point_time))]

        H.add_data_set(trading_point_level_3_dict,'flags',style = dict(fontSize = '0.6em'), shape = 'circlepin',name = 'trading_point_L3')
        #, onSeries = 'trend_prices_low_level'

        trading_point_time = trading_point_short.DATETIME.tolist()
        #使用确立时间
#         trading_point_time = trading_point_short.trading_point_time.tolist()
        trading_point_level_3_dict = [dict(x=trading_point_time[i], text = 'trading_point_3',title = 'S3') for i in range(0,len(trading_point_time))]

        H.add_data_set(trading_point_level_3_dict,'flags',style = dict(fontSize = '0.6em'), shape = 'squarepin',name = 'trading_point_S3')
        #, onSeries = 'trend_prices_low_level'

        return H


    def strategy_draw_v0828(param):
        '''
        根据pivot_start 和 pivot_end 绘图
        '''
        
        code = param['code']
        start = param['start']
        end = param['end']
#         py_path0 = param['py_path0']
        save_name0 = param['save_name0']
        k_min_high_level = param['k_min_high_level']
        k_min_low_level = param['k_min_low_level']
#         prices_start = param['prices_start']
#         prices_end = param['prices_end']
        end1 = (pd.Timestamp(end) + datetime.timedelta(days=1)).strftime('%Y%m%d')
        use_tick_merge = param['use_tick_merge'] #使用tick合成的K线：True，使用lab平台的数据：False

        #回测交易数据
        # logs_df0 = pd.read_csv('./circle/logs_'+save_name0+start+'_'+end+'.csv')
        # trades_df0 = pd.read_csv('./circle/trades_'+save_name0+start+'_'+end+'.csv')
        # trades_df0,logs_df0 = roll_test.init_handle(trades_df0,logs_df0)
        trades_df0 = pd.read_pickle('./第三买卖点/strategy_save/trades_'+save_name0+start+'_'+end+'.pkl')
        logs_df0 = pd.read_pickle('./第三买卖点/strategy_save/logs_'+save_name0+start+'_'+end+'.pkl')

        #高级K线数据:中枢
        part_high_level0 = pd.read_pickle(f'./第三买卖点/strategy_save/prices_part_high_level_{save_name0}_{start}_{end}.pkl' )
        pivot_high_level0 = pd.read_pickle(f'./第三买卖点/strategy_save/pivot_df_{save_name0}_{start}_{end}.pkl' )

        #低级K线数据:笔
        part_low_level0 = pd.read_pickle(f'./第三买卖点/strategy_save/prices_part_{save_name0}_{start}_{end}.pkl' )
        trend_prices_low_level0 =  MeanReversion.pen_point_prices(part_low_level0,False) # 默认是False

        #三买数据
        trading_point0 = pd.read_pickle(f'./第三买卖点/strategy_save/three_point_df_{save_name0}_{start}_{end}.pkl' )


        # # 保存计算数据
        # part_low_level0.to_pickle(f'./第三买卖点/vs/{save_name0}_part_low_level0_{start}_{end}.pkl')
        # pivot_high_level0.to_pickle(f'./第三买卖点/vs/{save_name0}_pivot_high_level0_{start}_{end}.pkl')
        # trading_point0.to_pickle(f'./第三买卖点/vs/{save_name0}_trading_point0_{start}_{end}.pkl')

        #### 二，价格合并，形成顶底分型、笔、走势中枢

        #### 2.1形成高级k线的中枢

        pivot = pivot_high_level0.copy()

        pivot['last_pivot_end'] = pivot['last_pivot_end'].fillna(method='backfill')
        pivot.dropna(subset = ['zd','zg'],how = 'any', inplace=True)
        pivot.drop_duplicates( inplace=True)
#         print(pivot)



        # pivot_fill = pivot.fillna(method='backfill')
        # filter_index = [i for i in pivot_fill.index if (pivot_fill.loc[i, 'last_pivot_end'] is None or
        #                                                 pivot_fill.loc[i, 'DATETIME'] <= pivot_fill.loc[
        #                                                     i, 'last_pivot_end'])]
        # pivot_fill = pivot_fill.reindex(filter_index)
        pivot = pivot.rename(columns={'last_pivot_end': 'pivot_end'})

        pivot.reset_index(drop=True, inplace=True)
        pivot_all= pivot.copy()

        pivot_prices_sigle = pivot_all.drop_duplicates(subset = ['pivot_start','pivot_end'],keep='last')

        # pivot_prices_sigle = pivot_all[pivot_all[['DATETIME', 'pivot_end']].assign(\
        #             NE=pivot_all.DATETIME.astype(str) == pivot_all.pivot_end.astype(str))['NE']]
#         prices_high_level0 = pd.read_pickle(f'./第三买卖点/{k_min_high_level}minK_20190102_20191231.pkl')

        if use_tick_merge:
            # #取部分使用tick合成的K线数据
            prices_high_level0 = K_cut.long_Kline_merge(start = start,end = end1,k_min = k_min_high_level)

        else:
            
            prices_high_level0 = DataProcess.get_lab_kline(start = start,end = end ,k_min_high_level = k_min_high_level)
#             class ContFutureSymbolFilter(D.FutContContractFilter):
#                 @staticmethod
#                 def future_suffix_replace(symbol_str: str):
#                     return symbol_str if '.CFE' not in symbol_str[0] else [symbol_str[0].replace(".CFE", ".CF")]

#                 def symbols_during(self, start_dt: str, end_dt: str):
#                     main_contracts_df = self._query_main_contract(symbols=self.symbols, start=start_dt, end=end_dt)
#                     if not main_contracts_df.empty:
#                         cont_list = []
#                         for i in range(len(main_contracts_df)):
#                             sub_cont = (main_contracts_df.iloc[i].symbol, main_contracts_df.iloc[i].start,
#                                         main_contracts_df.iloc[i].end, self.future_suffix_replace([main_contracts_df.iloc[i].mapping_symbol]))
#                             cont_list.append(sub_cont)
#                     return cont_list
                
#             #使用lab平台数据。
#             prices0 = D.query_tsdata(datasource=f'future_kline_{k_min_high_level}min', symbols=ContFutureSymbolFilter(code), fields='*', start=start, end=end)
#             prices_list = []
#             for df in prices0:
#     #             #xhq modify
#     #             df.index = pd.Series(df.index).shift(-1)
#     #             df = df.iloc[:-1,:]
#     #             ###
#                 prices_list.append(df)
#             prices_df = pd.concat(prices_list)

#             prices_high_level0 = prices_df[['Symbol', 'open', 'high', 'low', 'close']]
#             prices_high_level0.reset_index(inplace=True)
#             prices_high_level0 = prices_high_level0.rename(columns={'index':'DATETIME', 'Symbol': 'code'}) 
#         print(prices_high_level0)

        ##########

        pivot_prices = prices_high_level0.copy()
        pivot_prices['zd'] = np.nan
        pivot_prices['zg'] = np.nan
        pivot_prices.index = pivot_prices['DATETIME']
        for i in pivot_prices_sigle.index:
            pivot_prices.loc[pivot_prices_sigle.loc[i, 'pivot_start']:pivot_prices_sigle.loc[i, 'pivot_end'], 'zd'] \
                = pivot_prices_sigle.loc[i, 'zd']
            pivot_prices.loc[pivot_prices_sigle.loc[i, 'pivot_start']:pivot_prices_sigle.loc[i, 'pivot_end'], 'zg'] \
                = pivot_prices_sigle.loc[i, 'zg']
        pivot_prices = pivot_prices[['DATETIME', 'zd', 'zg']]
        pivot_prices.reset_index(drop=True, inplace=True)
        pivot_high_level = pivot_prices.copy()

        #### 2.2形成低级k线的笔

        trend_prices_low_level = trend_prices_low_level0.copy()

        ####  2.3 高级中枢+ 低级笔 = 三买

        trading_point  = trading_point0.drop_duplicates(subset = ['DATETIME']).copy()
        trading_point = trading_point[(trading_point['trading_point'] == 3 )|\
                                            (trading_point['trading_point'] == -3)]

        #### 三、画图:低级K线

        p_start = start
        p_end = end
        
        if use_tick_merge:
            # #取部分使用tick合成的K线数据数据绘图
#             prices_low_level0 = pd.read_pickle(f'./第三买卖点/{k_min_low_level}minK_{prices_start}_{prices_end}.pkl')
            #取start到end（包含end）的数据需要输入参数：start和end1
            prices_low_level0 = K_cut.long_Kline_merge(start = start,end = end1,k_min = k_min_low_level)

#             ##取部分数据

#             prices_low_level = prices_low_level0[(prices_low_level0['DATETIME'] <= end1)&
#                                                 (prices_low_level0['DATETIME'] >= start)].copy()
            prices = prices_low_level0
            H = ResultAssese.FigTradesSig_update_prices(code,p_start,p_end,trades_df0,logs_df0,prices,title =save_name0)
        else:
            #使用lab平台数据绘制低级k线。
            H = ResultAssese.FigTradesSig_update(code,p_start,p_end,trades_df0,logs_df0)








        #### 四、绘图：高级中枢、低级笔、交易点

        #低级K线trend（笔）
        trend_prices_low_level_list = trend_prices_low_level[['DATETIME','prices']].values.tolist()
        H.add_data_set(trend_prices_low_level_list, 'line', name = 'trend_prices_low_level', id='trend_prices_low_level')

        pivot_high_level_list = pivot_high_level[['DATETIME', 'zg', 'zd']].values.tolist()
        H.add_data_set(pivot_high_level_list, 'arearange', name = 'pivot_high_level')

        trading_point = trading_point
        trading_point_long = trading_point[trading_point['trading_point'] == 3]
        trading_point_short = trading_point[trading_point['trading_point'] == -3]

        trading_point_time = trading_point_long.DATETIME.tolist()
#         #使用确立时间
#         trading_point_time = trading_point_long.trading_point_time.tolist()
        trading_point_level_3_dict = [dict(x=trading_point_time[i], text = 'trading_point_3',title = 'L3') for i in range(0,len(trading_point_time))]

        H.add_data_set(trading_point_level_3_dict,'flags',style = dict(fontSize = '0.6em'), shape = 'circlepin',name = 'trading_point_L3')
        #, onSeries = 'trend_prices_low_level'

        trading_point_time = trading_point_short.DATETIME.tolist()
        #使用确立时间
#         trading_point_time = trading_point_short.trading_point_time.tolist()
        trading_point_level_3_dict = [dict(x=trading_point_time[i], text = 'trading_point_3',title = 'S3') for i in range(0,len(trading_point_time))]

        H.add_data_set(trading_point_level_3_dict,'flags',style = dict(fontSize = '0.6em'), shape = 'squarepin',name = 'trading_point_S3')
        #, onSeries = 'trend_prices_low_level'
        
        #加上确立时间标注
        pivot_time_list = pivot_all['pivot_time'].drop_duplicates().to_list()
        pivot_time_dict = [dict(x=pivot_time_list[i], text = 'pivot_time',title = 'T') for i in range(0,len(pivot_time_list))]

        H.add_data_set(pivot_time_dict,'flags',style = dict(fontSize = '0.6em'), shape = 'squarepin',name = 'pivot_time')

        return H

    
    def strategy_draw_level2(param,level2 = True):
        '''
        绘制30min_1min三买策略的标识图
        level2 = True : 图中含有根据高级K线绘制的笔
        '''

        start = param['start']
        end = param['end']
        save_name0 = param['save_name0']
        H = three_point.strategy_draw_v0828(param)
        if level2:
            part_high_level0 = pd.read_pickle(f'./第三买卖点/strategy_save/prices_part_high_level_{save_name0}_{start}_{end}.pkl')
            trend_prices_high_level0 =  MeanReversion.pen_point_prices(part_high_level0,False)
            trend_prices_high_level = trend_prices_high_level0.copy()
            #高级K线trend（笔）
            trend_prices_high_level_list = trend_prices_high_level[['DATETIME','prices']].values.tolist()
            H.add_data_set(trend_prices_high_level_list, 'line', name = 'trend_prices_high_level', id='trend_prices_high_level')
        return H
        
    
class three_point_backtest:
    

    def read_df(save_name0,start,end):
        #获取trades_df,logs_df
        #跨合约的close qty=0，手动修改成1
        trades_df0 = pd.read_pickle('./第三买卖点/strategy_save/trades_'+save_name0+start+'_'+end+'.pkl')
        logs_df0 = pd.read_pickle('./第三买卖点/strategy_save/logs_'+save_name0+start+'_'+end+'.pkl')
        trades_df0['qty'] = 1
        if trades_df0['open_close'].iloc[-1] == 'OPEN':
            trades_df0 = trades_df0.iloc[:-1,:]
            logs_df0 = logs_df0[logs_df0.index <= trades_df0.index[-1]]
        return trades_df0,logs_df0
    

    def analysis(save_name0,start,end):
        trades_df0,logs_df0 = three_point_backtest.read_df(save_name0,start,end)
        ### 评估 ###
        long_res_dict0,long_fig_dict0 = backtest.evaluation(trades =trades_df0,logs = logs_df0,\
                                                 start = start,end =end,html_out = False,html_path = './draw/'+save_name0 )
        analysis_close0,analysis_close_res0 = backtest.analysis(trades_df0,logs_df0)

        return analysis_close0,analysis_close_res0,long_res_dict0,long_fig_dict0
    
    
    def draw(start,end,py_path0,save_name0,flag = 'date_time',level2 = True,save_html = False):
        #绘制带有标识的K线图
        param0 = {
        'start':start,
        'end' :end,
        'py_path0' :py_path0,
        'save_name0':save_name0,
        'k_min_high_level':1,
        'k_min_low_level':1,
        'prices_start':'20190102',
        'prices_end':'20191231',
        'code':"IC00.CFE",
        'use_tick_merge':True}
        H0 = three_point.strategy_draw_level2(param0,level2 = level2)
        if save_html:
            H0.save_file(f"""./第三买卖点/draw/trading_point_{save_name0}_{start}_{end}_{flag}""")
        return H0
    
    def draw_v0903(param0,flag = 'date_time',level2 = True,save_html = False):
        '''
        为三买回测绘制带有标识的K线图
        '''
        start = param0['start']
        end = param0['end']
        save_name0 = param0['save_name0']
        H0 = three_point.strategy_draw_level2(param0,level2 = level2)
        if save_html:
            H0.save_file(f"""./第三买卖点/draw/trading_point_{save_name0}_{start}_{end}_{flag}""")
        return H0

