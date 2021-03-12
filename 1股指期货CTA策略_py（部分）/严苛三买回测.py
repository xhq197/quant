'''
author : xie huiqin
updata_time : 2020/09/02
base: 30_1min_严苛三买_modify5.py
target: 
#######

中枢：30minKline，笔：1minKline
严苛三买，调用market_timing_lab_v0827;three_point_class_v0827

Intermediate process：
【0901】修改止损条件：跨合约可传递仓位、只要价格突破中枢的上限和下限即可止损，避免无量下跌或上涨的情况。
【0902】做中间存储，以便未来实现对于一些中断的回测，可以利用之前跑出的结果接续起来。
【0902】可选择直接使用平台Kline或者使用tick数据合成任意Kline
【0902】根据文婷的探索修正一些可能导致回测终止的问题，准备做两年半的长期回测
【0903】不同K线组合生成的三买都可以使用这个文件进行回测


流水账：
含14:59:00
接受在一个中枢多次形成三买
修改创新高逻辑
0813：修改无OS；csv导入；DATETIME相同的三买；与latest函数输出三买对应
0813:不同产品之间数据传递
0813：输出中枢和三买的df，为之后绘图做准备
0824:相对于three_pivot_end2修正主动平仓
0824:相对于three_pivot_end3修正传递上一产品交易信息
'''

from algoqi.api.default_api import *
import numpy as np
import pandas as pd
from algoqi.data import D

D.load()
import warnings

warnings.filterwarnings("ignore")

from interval_theory import interval, K_cut
from three_point_class_v0827 import three_point
# from market_timing_lab_v0827 import MeanReversion
from backtest_class import strategy

from datetime import timedelta


# import datetime


def on_init(init_param, ctx: Context, U: UserSpace):
    ctx.log("initialize params")  # 日志

    long_or_short: str = init_param['long_short']
    if long_or_short == 'long':
        symbol = init_param['symbol']
        symbols = symbol[:-1]  # .CF
    else:
        # tick数据是.CFE;1min_kline是.CF
        symbol: str = init_param['symbol']  # 初始化参数
        # 'IC00.CFE'
        symbols = symbol
        symbol = symbol + 'E'
    U.py_name :str = init_param['py_name']
    U.first_start: str = init_param['first_start']
    U.last_end: str = init_param['last_end']
    U.start: str = init_param['start']
        
    #latest_end:本次合约之前一个合约的结束日期
    U.latest_end : str = init_param['latest_end']
        
    U.end: str = init_param['end']
    U.per_size: int = init_param['per_size']
    U.k_min_high_level: int = init_param['k_min_high_level'] 
    U.k_min_low_level: int = init_param['k_min_low_level']
    U.use_tick_merge = init_param['use_tick_merge']
    #     N :int =  init_param['N']

    ctx.subscribe_tick([symbol], fields=[TickFields.TRADE_PRICE,
                                         TickFields.B1, TickFields.S1,
                                         TickFields.SV1, TickFields.BV1])

    ctx.subscribe_time("09:45:00", "market_start")  # 开盘前16min不开仓
    ctx.subscribe_time("11:30:00", "market_suspend")
    ctx.subscribe_time("13:00:00", "market_start")
    ctx.subscribe_time("15:00:00", "market_almost_close")  # 收盘前15min完全平仓 修改：收盘前30min只平仓不开仓

    today = ctx.today().strftime('%Y%m%d')


    if today == U.start:

#         #使用tick合成的一段时间K线（pkl文件）， 导入pkl，加快运行速度【数据1】
#         U.raw_prices = pd.read_pickle(f'./第三买卖点/{U.k_min_low_level}minK_20190102_20191231.pkl')
#         U.raw_prices_high_level = pd.read_pickle(f'./第三买卖点/{U.k_min_high_level}minK_20190102_20191231.pkl')

        #使用平台数据【数据2】或者使用【数据3】
        pass
        
        
#   【数据1】
#     now_date = ctx.today().strftime('%Y-%m-%d')
#     next_date = (ctx.today() + timedelta(days=1)).strftime('%Y-%m-%d')

#     prices = U.raw_prices[(U.raw_prices['DATETIME'] <= next_date) & (U.raw_prices['DATETIME'] >= now_date)]

#     prices_high_level = U.raw_prices_high_level[(U.raw_prices_high_level['DATETIME'] <= next_date)
#                                                 & (U.raw_prices_high_level['DATETIME'] >= now_date)]


    if U.use_tick_merge:
    #     使用tick合成的K线，每日计算【数据3】
        prices = K_cut.kline_merge_strategy(k_min = U.k_min_low_level,start_date = today,symbols=[symbol])
        prices_high_level = K_cut.kline_merge_strategy(k_min = U.k_min_high_level,start_date = today,symbols=[symbol])

        
    else:
    #   【数据2】
        curDate = ctx.today().strftime('%Y%m%d')

        data = D.query_tsdata(datasource=f'future_kline_{U.k_min_low_level}min', symbols=[symbols], fields = ['open','high','low','close'],\
        start = curDate, end=curDate, delivery_mode=D.DataDeliveryMode.DIRECT)

        data_high_level = D.query_tsdata(datasource=f'future_kline_{U.k_min_high_level}min', symbols=[symbols], fields = ['open','high','low','close'],\
        start = curDate, end=curDate, delivery_mode=D.DataDeliveryMode.DIRECT)
        try:
            # 检查是否发生数据缺失，缺失则跳过
            data = data.reset_index()
            data_high_level = data_high_level.reset_index()

        except AttributeError:
            print('\n',curDate,'：数据缺失，跳过该日。')
            return
        
        prices = data.rename(columns={'Symbol': 'code', 'index': 'DATETIME'})
        prices_high_level = data_high_level.rename(columns={'Symbol': 'code', 'index': 'DATETIME'})
#         print(prices_high_level.iloc[:10,:])
        
    if len(prices) == 0 or len(prices_high_level) == 0:
        return



    ###input###
    # 计算每天前15min的数据

    if today == U.start:
        if today == U.first_start:
            #创建存储文件夹
            try:
                import os 
                os.mkdir(f'./第三买卖点/strategy_save/{U.py_name}_{U.first_start}_{U.last_end}')
            except FileExistsError:
                pass
                
            U.high_level_begin_time = prices_high_level['DATETIME'].iloc[0].strftime('%Y-%m-%d %H:%M:%S')

            # 回测第一天，计算初始值
            U.last_trading_point_time = 'init_trading_point_time'
            U.last_open = 'init_open'
            # 初始化中枢和三买df
            U.pivot_df = pd.DataFrame()
            U.three_point_df = pd.DataFrame()

            prices_init = prices[prices['DATETIME'] <= U.high_level_begin_time]
            prices_init_high_level = prices_high_level[prices_high_level['DATETIME'] <= U.high_level_begin_time]

            prices_adj, prices_part, prices_adj_high_level, prices_part_high_level, pivot_latest, trading_point_level_3 \
                = three_point.three_point_init_level2(prices_init, prices_init_high_level)

            U.pivot_df = U.pivot_df.append(pd.DataFrame({U.high_level_begin_time: pivot_latest}).T)
            
            if trading_point_level_3 != {}:
                U.three_point_df = U.three_point_df.append(
                    pd.DataFrame({U.high_level_begin_time: trading_point_level_3}).T)
            
            if pd.Timestamp(U.first_start + ' 09:45:00').strftime('%Y-%m-%d %H:%M:%S') > U.high_level_begin_time:
                prices_init = prices[(U.high_level_begin_time < prices['DATETIME'] )&(prices['DATETIME'] <= today+ ' 09:45:00')]
#                 print('\n*****',prices_init)
                for datetime in prices_init['DATETIME']:
                    prices_latest = prices.loc[prices['DATETIME'] == datetime, :]
                    prices_latest_high_level = prices_high_level.loc[prices_high_level['DATETIME'] == datetime, :]
                    prices_adj, prices_part, prices_adj_high_level, prices_part_high_level, pivot_latest, trading_point_level_3 = \
                        three_point.three_point_latest_level2_v0827(prices_latest, prices_latest_high_level, prices_adj,
                                                              prices_part, \
                                                              prices_adj_high_level, prices_part_high_level, pivot_latest,
                                                              trading_point_level_3)

                    U.pivot_df = U.pivot_df.append(pd.DataFrame({datetime.strftime('%Y-%m-%d %H:%M:%S'): pivot_latest}).T)
                    if trading_point_level_3 != {}:
                        U.three_point_df = U.three_point_df.append(
                            pd.DataFrame({datetime.strftime('%Y-%m-%d %H:%M:%S'): trading_point_level_3}).T)
            else:
                pass
            U.compare_time = max(pd.Timestamp(U.first_start + ' 09:45:00').strftime('%Y-%m-%d %H:%M:%S'),U.high_level_begin_time)



        else:
            # 承接上一产品信息
            prices_adj = pd.read_pickle(
                f'./第三买卖点/strategy_save/{U.py_name}_{U.first_start}_{U.last_end}/prices_adj_{U.py_name}_{U.first_start}_{U.latest_end}.pkl')
            prices_part = pd.read_pickle(
                f'./第三买卖点/strategy_save/{U.py_name}_{U.first_start}_{U.last_end}/prices_part_{U.py_name}_{U.first_start}_{U.latest_end}.pkl')
            prices_adj_high_level = pd.read_pickle(
                f'./第三买卖点/strategy_save/{U.py_name}_{U.first_start}_{U.last_end}/prices_adj_high_level_{U.py_name}_{U.first_start}_{U.latest_end}.pkl')
            prices_part_high_level = pd.read_pickle(
                f'./第三买卖点/strategy_save/{U.py_name}_{U.first_start}_{U.last_end}/prices_part_high_level_{U.py_name}_{U.first_start}_{U.latest_end}.pkl')

            pivot_latest_series = pd.read_pickle(
                f'./第三买卖点/strategy_save/{U.py_name}_{U.first_start}_{U.last_end}/pivot_latest_{U.py_name}_{U.first_start}_{U.latest_end}.pkl')
#             pivot_latest = pivot_latest_series.to_dict()
            pivot_latest  = strategy.dict_no_nat(pivot_latest_series)

            trading_point_series = pd.read_pickle(
                f'./第三买卖点/strategy_save/{U.py_name}_{U.first_start}_{U.last_end}/trading_point_level_3_{U.py_name}_{U.first_start}_{U.latest_end}.pkl')
#             trading_point_level_3 = trading_point_series.to_dict()
            trading_point_level_3  = strategy.dict_no_nat(trading_point_series)


            last_point_series = pd.read_pickle(
                f'./第三买卖点/strategy_save/{U.py_name}_{U.first_start}_{U.last_end}/last_trading_point_time_{U.py_name}_{U.first_start}_{U.latest_end}.pkl')
            
            U.last_trading_point_time = last_point_series.iloc[0]
            U.last_open = last_point_series.iloc[1]
            U.can_close = last_point_series.iloc[2]
            U.last_pivot = last_point_series.iloc[3]
#             print('\n','in_pivot:',U.last_pivot,'\n',last_point_series)


            U.pivot_df = pd.read_pickle(f'./第三买卖点/strategy_save/{U.py_name}_{U.first_start}_{U.last_end}/pivot_df_{U.py_name}_{U.first_start}_{U.latest_end}.pkl')
            U.three_point_df = pd.read_pickle(
                f'./第三买卖点/strategy_save/{U.py_name}_{U.first_start}_{U.last_end}/three_point_df_{U.py_name}_{U.first_start}_{U.latest_end}.pkl')


            prices_init = prices[prices['DATETIME'] < today + ' 09:45:00']
            for datetime in prices_init['DATETIME']:
                prices_latest = prices.loc[prices['DATETIME'] == datetime, :]
                prices_latest_high_level = prices_high_level.loc[prices_high_level['DATETIME'] == datetime, :]
                prices_adj, prices_part, prices_adj_high_level, prices_part_high_level, pivot_latest, trading_point_level_3 = \
                    three_point.three_point_latest_level2(prices_latest, prices_latest_high_level, prices_adj,
                                                          prices_part, \
                                                          prices_adj_high_level, prices_part_high_level, pivot_latest,
                                                          trading_point_level_3)

                U.pivot_df = U.pivot_df.append(pd.DataFrame({datetime.strftime('%Y-%m-%d %H:%M:%S'): pivot_latest}).T)
                if trading_point_level_3 != {}:
                    U.three_point_df = U.three_point_df.append(
                        pd.DataFrame({datetime.strftime('%Y-%m-%d %H:%M:%S'): trading_point_level_3}).T)




    elif today != U.start:
        # 承接同一产品中上一日的信息
        prices_adj = U.prices_adj
        prices_part = U.prices_part
        prices_adj_high_level = U.prices_adj_high_level
        prices_part_high_level = U.prices_part_high_level
        pivot_latest = U.pivot_latest
        trading_point_level_3 = U.trading_point_level_3

        prices_init = prices[prices['DATETIME'] < today + ' 09:45:00']
        for datetime in prices_init['DATETIME']:
            prices_latest = prices.loc[prices['DATETIME'] == datetime, :]
            prices_latest_high_level = prices_high_level.loc[prices_high_level['DATETIME'] == datetime, :]
            prices_adj, prices_part, prices_adj_high_level, prices_part_high_level, pivot_latest, trading_point_level_3 = \
                three_point.three_point_latest_level2(prices_latest, prices_latest_high_level, prices_adj, prices_part, \
                                                      prices_adj_high_level, prices_part_high_level, pivot_latest,
                                                      trading_point_level_3)
            U.pivot_df = U.pivot_df.append(pd.DataFrame({datetime.strftime('%Y-%m-%d %H:%M:%S'): pivot_latest}).T)
            if trading_point_level_3 != {}:
                U.three_point_df = U.three_point_df.append(
                    pd.DataFrame({datetime.strftime('%Y-%m-%d %H:%M:%S'): trading_point_level_3}).T)

    U.prices = prices
    U.prices_high_level = prices_high_level
    U.current_state = "WAITING"
#     U.per_size = per_size
    U.symbol = symbol  # .CFE
    U.symbols = symbols  # .CF

    U.prices_adj = prices_adj
    U.prices_part = prices_part
    U.prices_adj_high_level = prices_adj_high_level
    U.prices_part_high_level = prices_part_high_level
    U.pivot_latest = pivot_latest
    U.trading_point_level_3 = trading_point_level_3

    U.date = 'date_init'

    U.today = today
#     U.start = start
#     U.end = end

    ######


def on_data_update(ctx: Context, U: UserSpace):
    if U.current_state != 'EXECUTING':
        return
    symbol = U.symbol
#     per_size = U.per_size
    pos_short = ctx.get_position(symbol, LongShortType.SHORT)
    pos_long = ctx.get_position(symbol, LongShortType.LONG)
    price_b1 = ctx.get_latest_value(symbol, TickFields.B1)
    price_s1 = ctx.get_latest_value(symbol, TickFields.S1)

    if ((price_b1 is None) and (price_s1 is None)):
        return
    # 截取至此时的价格数据
    curtime = ctx.today().strftime('%Y-%m-%d %H:%M:%S')

    prices = U.prices
    prices = prices[prices['DATETIME'] <= curtime]
    ######
    # 现在考虑止损条件

#     if curtime >= '2019-06-21 09:30:00':
#         print('\n',curtime,'\n',U.last_pivot,'\n',price_b1,'\n',price_s1)
        
    # 存在多头仓位
    if pos_long.outstanding_open_qty == 0 \
            and pos_short.outstanding_open_qty == 0 \
            and pos_short.hold_qty_total == 0 \
            and (pos_long.hold_qty_total == U.per_size or U.last_open == 'Long'):
        #         if prices.iloc[-1]['low'] < U.down_parting:
        if price_b1 <= U.last_pivot['zg']:
            U.last_open = 'Close'
            ctx.close_position(symbol, LongShortType.LONG, ExchangeType.CFE, \
                               pos_long.hold_qty_total, price_b1)
            ctx.log('破底CL_{}'.format(price_b1))
            U.can_close = False
#             print('\n** 止损平多',curtime)
#             print('\n止损CL',curtime,'\n',U.last_pivot,'\n',price_b1,'\n',price_s1)
        else:
            pass

    # 存在空头仓位
    elif pos_long.outstanding_open_qty == 0 \
            and pos_short.outstanding_open_qty == 0 \
            and pos_long.hold_qty_total == 0 \
            and (pos_short.hold_qty_total == U.per_size or U.last_open == 'Short'):
        #         if prices.iloc[-1]['high'] > U.up_parting:
        if price_s1 >= U.last_pivot['zd'] :
            U.last_open = 'Close'
            ctx.close_position(symbol, LongShortType.SHORT, ExchangeType.CFE, \
                               pos_short.hold_qty_total, price_s1)
            ctx.log('破顶CS_{}'.format(price_s1))
#             print('\n** 止损平空',curtime)
            U.can_close = False
#             print('\n止损CS',curtime,'\n',U.last_pivot,'\n',price_b1,'\n',price_s1)
        else:
            pass

        
    if not (curtime[-2:] == '00'):
        return
    
    if U.today == U.first_start:
        if curtime <= U.compare_time:
            return


    ####input####

    prices_high_level = U.prices_high_level
    prices_adj = U.prices_adj
    prices_part = U.prices_part
    prices_adj_high_level = U.prices_adj_high_level
    prices_part_high_level = U.prices_part_high_level
    pivot_latest = U.pivot_latest
    trading_point_level_3 = U.trading_point_level_3

    if curtime != U.date:
        # 计算第三买卖点
#         print('\n222',curtime)
        prices_latest = prices.loc[prices['DATETIME'] == curtime, :]
        prices_latest_high_level = prices_high_level.loc[prices_high_level['DATETIME'] == curtime, :]

        prices_adj, prices_part, prices_adj_high_level, prices_part_high_level, pivot_latest, trading_point_level_3 \
            = three_point.three_point_latest_level2_v0827(prices_latest, \
                                                    prices_latest_high_level, prices_adj, prices_part,
                                                    prices_adj_high_level, \
                                                    prices_part_high_level, pivot_latest, trading_point_level_3)

        U.pivot_df = U.pivot_df.append(pd.DataFrame({curtime: pivot_latest}).T)
        if trading_point_level_3 != {}:
            U.three_point_df = U.three_point_df.append(pd.DataFrame({curtime: trading_point_level_3}).T)
        U.prices_adj = prices_adj
        U.prices_part = prices_part
        U.prices_adj_high_level = prices_adj_high_level
        U.prices_part_high_level = prices_part_high_level
        U.pivot_latest = pivot_latest
        U.trading_point_level_3 = trading_point_level_3


    U.date = curtime


    # 开仓条件和平仓条件要分开写，一秒钟内可以进2tick数据，所以可以在一秒内先后平仓再开仓，且第二个tick不做交易信号计算
    # 开仓条件
    current_t = pd.to_datetime(curtime)
    close_t = pd.to_datetime(ctx.today().strftime('%Y-%m-%d') + ' 15:00:00')
    delta_close = close_t - current_t  # 收盘前半小时不交易

    if len(prices_part) <= 1:
        return


    # 开平仓
    if trading_point_level_3 != {} \
            and pos_long.outstanding_open_qty == 0 \
            and pos_short.outstanding_open_qty == 0 \
            and pos_short.hold_qty_total == 0 \
            and pos_long.hold_qty_total == 0 \
            and delta_close.total_seconds() > 1800 \
            and trading_point_level_3['DATETIME'] != U.last_trading_point_time\
            and U.last_open != 'Long' \
            and U.last_open != 'Short':
        
        if trading_point_level_3['trading_point'] == 3:
            # tick数据是CFE,多头开仓
            ctx.open_order(symbol, LongShortType.LONG, ExchangeType.CFE, U.per_size, price_s1)


            U.last_open = 'Long'
            U.can_close = True
            ctx.log('OL_{}'.format(price_s1))
            U.last_trading_point_time = trading_point_level_3['DATETIME']
            #modify：v0827：先计算三买，再计算中枢，U.last_pivot统一取倒数第二行
            U.last_pivot = U.pivot_df.iloc[-2,:].to_dict()
#             print('\n开多****',curtime)
#             print('\n开多****',curtime,'\n',U.last_pivot ,'\n',U.pivot_latest,'\n',U.prices_part.iloc[-15:,:],'\n', U.trading_point_level_3)


            


        elif trading_point_level_3['trading_point'] == -3:
            ctx.open_order(symbol, LongShortType.SHORT, ExchangeType.CFE, U.per_size, price_b1)  # 空头开仓


            U.last_open = 'Short'
            U.can_close = True
            ctx.log('OS_{}'.format(price_b1))
            U.last_trading_point_time = trading_point_level_3['DATETIME']
            #modify：v0827：先计算三买，再计算中枢，U.last_pivot统一取倒数第二行
            U.last_pivot = U.pivot_df.iloc[-2,:].to_dict()
#             print('\n开空****',curtime)
#             print('\n开空****',curtime,'\n',U.last_pivot ,'\n',U.pivot_latest,'\n',U.prices_part.iloc[-15:,:],'\n', U.trading_point_level_3)


    elif pos_long.outstanding_open_qty == 0 \
            and pos_short.outstanding_open_qty == 0 \
            and (pos_short.hold_qty_total == U.per_size or U.last_open == 'Short')\
            and pos_long.hold_qty_total == 0 \
            and U.can_close:
        
        if not((pivot_latest['zd'] is None) or (pivot_latest['zg'] is None)):
            if pivot_latest['zd'] > 0 and pivot_latest['zg'] > 0:
                if pivot_latest['pivot_start'] > U.last_pivot['pivot_start']:
                    U.last_open = 'Close'
                    ctx.close_position(symbol, LongShortType.SHORT, ExchangeType.CFE,\
                                        pos_short.hold_qty_total, price_s1)  # 空头平仓
                    ctx.log('CS_{}'.format(price_s1))
#                     print('\n** 平空',curtime)
        

    elif pos_long.outstanding_open_qty == 0 \
            and pos_short.outstanding_open_qty == 0 \
            and pos_short.hold_qty_total == 0 \
            and (pos_long.hold_qty_total == U.per_size or U.last_open == 'Long') \
            and U.can_close:
                    
        if not((pivot_latest['zd'] is None) or (pivot_latest['zg'] is None)):
            if pivot_latest['zd'] > 0 and pivot_latest['zg'] > 0:
                if pivot_latest['pivot_start'] > U.last_pivot['pivot_start']:
                    U.last_open = 'Close'
                    ctx.close_position(symbol, LongShortType.LONG, ExchangeType.CFE, \
                                        pos_long.hold_qty_total, price_b1)  # 多头平仓
                    ctx.log('CL_{}'.format(price_b1))
#                     print('\n** 平多',curtime)
                    

    else:
        pass

        


def on_schedule(sched: str, ctx: Context, U: UserSpace):
    if sched == 'market_start':
        U.current_state = 'EXECUTING'
    elif sched == 'market_suspend':
        U.current_state = 'WAITING'
    elif sched == 'market_almost_close':
        U.current_state = 'ENDED'

        for order in ctx.get_all_orders():
            if not order.is_in_terminal_state():
                ctx.cancel_order(order.order_id)


def on_stop(ctx: Context, U: UserSpace):
    compare_last_end = pd.Timestamp(U.last_end) - timedelta(days=5)
    # 跨产品传递信息
    if U.end == ctx.today().strftime('%Y%m%d') \
            or ctx.today().strftime('%Y%m%d') >= compare_last_end.strftime('%Y%m%d'):
        
        #存储1：方便在回测过程中进行回测评估
        U.prices_adj.to_pickle(f'./第三买卖点/strategy_save/prices_adj_{U.py_name}_{U.first_start}_{U.last_end}.pkl')
        U.prices_part.to_pickle(f'./第三买卖点/strategy_save/prices_part_{U.py_name}_{U.first_start}_{U.last_end}.pkl')
        U.prices_adj_high_level.to_pickle(
            f'./第三买卖点/strategy_save/prices_adj_high_level_{U.py_name}_{U.first_start}_{U.last_end}.pkl')
        U.prices_part_high_level.to_pickle(
            f'./第三买卖点/strategy_save/prices_part_high_level_{U.py_name}_{U.first_start}_{U.last_end}.pkl')
        pivot_latest_series = pd.Series(U.pivot_latest)
        pivot_latest_series.to_pickle(
            f'./第三买卖点/strategy_save/pivot_latest_{U.py_name}_{U.first_start}_{U.last_end}.pkl')

        trading_point_series = pd.Series(U.trading_point_level_3)
        trading_point_series.to_pickle(
            f'./第三买卖点/strategy_save/trading_point_level_3_{U.py_name}_{U.first_start}_{U.last_end}.pkl')

        last_point_series = pd.Series({0: U.last_trading_point_time,1:U.last_open,2:U.can_close,3:U.last_pivot})
        last_point_series.to_pickle(
            f'./第三买卖点/strategy_save/last_trading_point_time_{U.py_name}_{U.first_start}_{U.last_end}.pkl')
#         print('\n','out_pivot:',U.last_pivot,'\n',last_point_series)
        U.pivot_df.to_pickle(f'./第三买卖点/strategy_save/pivot_df_{U.py_name}_{U.first_start}_{U.last_end}.pkl')
        U.three_point_df.to_pickle(f'./第三买卖点/strategy_save/three_point_df_{U.py_name}_{U.first_start}_{U.last_end}.pkl')
        
        #存储2：做中间存储，方便从任何一个合约开始接着回测。
        U.prices_adj.to_pickle(f'./第三买卖点/strategy_save/{U.py_name}_{U.first_start}_{U.last_end}/prices_adj_{U.py_name}_{U.first_start}_{U.end}.pkl')
        U.prices_part.to_pickle(f'./第三买卖点/strategy_save/{U.py_name}_{U.first_start}_{U.last_end}/prices_part_{U.py_name}_{U.first_start}_{U.end}.pkl')
        U.prices_adj_high_level.to_pickle(
            f'./第三买卖点/strategy_save/{U.py_name}_{U.first_start}_{U.last_end}/prices_adj_high_level_{U.py_name}_{U.first_start}_{U.end}.pkl')
        U.prices_part_high_level.to_pickle(
            f'./第三买卖点/strategy_save/{U.py_name}_{U.first_start}_{U.last_end}/prices_part_high_level_{U.py_name}_{U.first_start}_{U.end}.pkl')
        pivot_latest_series = pd.Series(U.pivot_latest)
        pivot_latest_series.to_pickle(
            f'./第三买卖点/strategy_save/{U.py_name}_{U.first_start}_{U.last_end}/pivot_latest_{U.py_name}_{U.first_start}_{U.end}.pkl')

        trading_point_series = pd.Series(U.trading_point_level_3)
        trading_point_series.to_pickle(
            f'./第三买卖点/strategy_save/{U.py_name}_{U.first_start}_{U.last_end}/trading_point_level_3_{U.py_name}_{U.first_start}_{U.end}.pkl')

        last_point_series = pd.Series({0: U.last_trading_point_time,1:U.last_open,2:U.can_close,3:U.last_pivot})
        last_point_series.to_pickle(
            f'./第三买卖点/strategy_save/{U.py_name}_{U.first_start}_{U.last_end}/last_trading_point_time_{U.py_name}_{U.first_start}_{U.end}.pkl')
#         print('\n','out_pivot:',U.last_pivot,'\n',last_point_series)
        U.pivot_df.to_pickle(f'./第三买卖点/strategy_save/{U.py_name}_{U.first_start}_{U.last_end}/pivot_df_{U.py_name}_{U.first_start}_{U.end}.pkl')
        U.three_point_df.to_pickle(f'./第三买卖点/strategy_save/{U.py_name}_{U.first_start}_{U.last_end}/three_point_df_{U.py_name}_{U.first_start}_{U.end}.pkl')
#     if  ctx.today().strftime('%Y%m%d') >= '20190225':  
#         print('\n检查end',U.last_end,ctx.today().strftime('%Y%m%d'))
    if U.last_end == ctx.today().strftime('%Y%m%d'):
        #需要回测终点为产品到期日
        #最后一笔强制平仓
#         if ctx.today().strftime('%Y%m%d') >= compare_last_end.strftime('%Y%m%d'):
        pos_short = ctx.get_position(U.symbol, LongShortType.SHORT)
        pos_long = ctx.get_position(U.symbol, LongShortType.LONG)

        price_b1 = ctx.get_latest_value(U.symbol, TickFields.B1)
        price_s1 = ctx.get_latest_value(U.symbol, TickFields.S1)
        if pos_short.hold_qty_total > 0:
            ctx.close_position(U.symbol, LongShortType.SHORT, ExchangeType.CFE, pos_short.hold_qty_total, price_s1)
            ctx.log('end_CS_{}'.format(price_s1))
        if pos_long.hold_qty_total > 0:
            ctx.close_position(U.symbol, LongShortType.LONG, ExchangeType.CFE, pos_long.hold_qty_total, price_b1)
            ctx.log('end_CL_{}'.format(price_b1))

    ctx.log('stop strategy')
    
