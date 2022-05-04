'''
#-*- coding: utf-8 -*-
@Author  : xiehuiqin
@Time    : 2022/1/27 2:12
@Function: 交易模块
按照20170114指数权重买卖股票。
'''

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from JUDGE import judge_model
from VIS import ReversePointVis
from CNN import runCNN
from DATA import handleData
class IndexTrade:
    def __init__(self,open_df,weights,trade_signal):
        self.open_df = open_df
        self.weights = weights
        self.trade_signal = trade_signal

    def buy_basket(self,capital,dt):
        '''
        :param capital:
        :return: basket:{<stock_code>:<stock_number,手>}  capital_res
        '''

        basket = {code:0 for code in self.weights}
        capital_res = 0
        for code in basket:
            code_capital = capital * self.weights[code]
            code_open = float(self.open_df.loc[dt,code])
            if code_open != 0:
                basket[code] = (code_capital/code_open )//100
                capital_res += code_capital -  basket[code] * 100 * code_open
            else:
                capital_res += code_capital

        return basket,capital_res

    def sell_basket(self,basket,dt):
        '''
        :param basket: {<stock_code>:<stock_number>}
        :return: capital_from_sell
        '''
        capital_from_sell = 0
        for code in basket:
            code_open = self.open_df.loc[dt,code]
            capital_from_sell += basket[code] *code_open*100
        return capital_from_sell

    def trade(self,capital,tarCount):
        '''
        连续第tarCount个交易点才考虑交易，先买入后卖出。
        :param capital: 初始资金(RMB)
        :param tarCount: 连续第几个交易点才开始交易
        :return: log:{date:<>,captial:<>}

        '''
        count = [0,0]
        log = pd.DataFrame(index = self.open_df.index,columns=['type','capital'])
        is_buy = False
        for dt in self.trade_signal.index:
            if self.trade_signal.loc[dt,'signal'] == -1:
                if count[1] != 0:
                    count[1] = 0
                count[0] += 1
                if count[0] == tarCount and not is_buy:
                    basket,capital_res = self.buy_basket(capital,dt)
                    log.loc[dt,'type'] = 'buy'
                    log.loc[dt,'capital'] = capital
                    is_buy = True
            elif self.trade_signal.loc[dt,'signal'] == 1:
                if count[0] != 0:
                    count[0] = 0
                count[1] += 1
                if count[1] == tarCount and is_buy:
                    capital = self.sell_basket(basket,dt) + capital_res
                    log.loc[dt,'type'] = 'sell'
                    log.loc[dt,'capital'] = capital
                    is_buy = False
        return log

    def trade1(self,capital,tarCount):
        '''
        连续第tarCount个交易点才考虑交易，先买入后卖出。
        :param capital: 初始资金(RMB)
        :param tarCount: 连续第几个交易点才开始交易
        :return: log:{date:<>,captial:<>}

        '''
        count = [0,0]
        log = pd.DataFrame(index = self.open_df.index,columns=['type','capital'])
        is_buy = False
        for dt in self.trade_signal.index:
            if self.trade_signal.loc[dt,'signal'] == 1:
                if count[1] != 0:
                    count[1] = 0
                count[0] += 1
                if count[0] == tarCount and not is_buy:
                    basket,capital_res = self.buy_basket(capital,dt)
                    log.loc[dt,'type'] = 'buy'
                    log.loc[dt,'capital'] = capital
                    is_buy = True
            elif self.trade_signal.loc[dt,'signal'] == -1:
                if count[0] != 0:
                    count[0] = 0
                count[1] += 1
                if count[1] == tarCount and is_buy:
                    capital = self.sell_basket(basket,dt) + capital_res
                    log.loc[dt,'type'] = 'sell'
                    log.loc[dt,'capital'] = capital
                    is_buy = False
        return log

class  run_trade:
    @staticmethod
    def myTradeMain(trade_signal,tarCount = 3):
        ## 打印完整df
        # pd.set_option('display.max_rows', 50000)
        # pd.set_option('display.max_columns', 50000)
        # pd.set_option('display.width', 2000)
        # 获取20170114成分股权重
        weights_df = pd.read_csv('./data/trade/sz50_open_170114.csv', skiprows=1,nrows = 2,index_col = 0).T
        weights_tmp = weights_df['weight'].to_dict()
        weights = {code:float(weights_tmp[code])/100 for code in weights_tmp}
        # print(weights)
        # 获取20170114-20220114开盘价
        open_df = pd.read_csv('./data/trade/sz50_open_170114.csv', skiprows=3,index_col = 0)
        open_df.index = pd.to_datetime(open_df.index)
        open_df = open_df[open_df.index >= '2017-01-14']

        # 获取交易信号
        # ## 模型一：加权复合模型
        # vic_data_1 = pd.read_csv('./res/20220126_1.csv',index_col = 0)
        # vic_data_m1 = pd.read_csv('./res/20220126_-1.csv',index_col = 0)
        # vic_data_m1['pre'] = -vic_data_m1['pre']
        # trade_signal = pd.merge(vic_data_1[['open','flag','pre']],vic_data_m1['pre'],left_index = True,right_index = True,how = 'left')
        # trade_signal['signal'] = trade_signal['pre_x'] + trade_signal['pre_y']
        # ## 模型二：CNN
        # trade_signal = pd.read_csv('./res/CNN20220128.csv',index_col= 0)
        # rC = runCNN(102,60)
        # trade_signal = rC.CNN_main()


        ReversePointVis.true_pre_plot(trade_signal.iloc[-600:,:],'True_VS_Pre2')
        ReversePointVis.true_pre_plot(trade_signal.iloc[:-600,:],'True_VS_Pre1')

        # 完整评估预测效果
        judge_df = trade_signal.copy()
        judge_df = judge_df[judge_df.index >= '2017-01-14']
        judge_df.dropna(how = 'any',inplace=True)
        # 使用shift +-1的标签target，原始标签为flag。
        judge_df['target'] = judge_df['flag']
        handleData.change_flag(judge_df,3)
        y_test =np.array(judge_df['target']).reshape(1, -1)[0]
        y_pre =np.array(judge_df['signal']).reshape(1, -1)[0]
        judge_model.evaluation(y_test,y_pre)
        # signal下移一天，变成当日开盘的交易信号。
        trade_signal['signal'] = trade_signal['signal'].shift(1)
        trade_signal.index = pd.to_datetime(trade_signal.index)
        trade_signal = trade_signal[trade_signal.index >= '2017-01-14']
        trade_signal = trade_signal[['open','signal']]
        # print(trade_signal.head())
        # print(trade_signal.tail())
        # print(trade_signal[trade_signal.signal != 0])




        capital = 100000000


        tr = IndexTrade(open_df,weights,trade_signal)
        log = tr.trade(capital,tarCount)
        log = log.merge(trade_signal['open'],left_index=True,right_index=True,how='left')
        draw_log = log.copy()
        log.dropna(subset = ['capital'],inplace=True)
        # log.to_csv('./res/log.csv')

        # 结果汇总
        print(log)

        print('####### res #######')
        print('策略年化收益率：{:.2%}'.format((log.iloc[-1]['capital']/capital - 1)/5))
        print('长期持有年化收益率：{:.2%}'.format((log.iloc[-1]['open']/log.iloc[0]['open'] - 1)/5))
        print('股指ETF基金平均年化收益率：{:.2%}'.format(0.1260))

        # 每年收益
        year_lst = [2018,2019,2020,2021,2022]
        yield_df = pd.DataFrame(index = ['yield'],columns=year_lst)
        for year in year_lst:
            year_log = log.loc[(log.index > str(year - 1) + '-01-14')&(log.index <= str(year) + '-01-14')]
            r = year_log.iloc[-1]['capital'] / year_log.iloc[0]['capital'] -1
            yield_df.loc['yield',year] = r
        yield_df.iloc[0,:] = yield_df.iloc[0,:].apply(lambda x:format(x,'.2%'))
        print(yield_df)

        # 可视化
        draw_log['capital'] = draw_log['capital'].fillna(method='ffill')
        draw_log['capital'] = draw_log['capital'].fillna(capital)
        draw_log.dropna(subset=['open'],inplace=True)

        plt.figure(figsize= (10,5))
        draw_log['buy_point'] = np.where(draw_log.type == 'buy',draw_log.open,np.nan)
        draw_log['sell_point'] = np.where(draw_log.type == 'sell',draw_log.open,np.nan)
        init_open = draw_log.iloc[0]['open']
        plt.plot(draw_log.index, draw_log.capital/capital,label = 'capital',alpha = 0.5)
        plt.plot(draw_log.index, draw_log.open / init_open,label = 'index_open',alpha = 0.5)
        plt.scatter(draw_log.index, draw_log.buy_point/ init_open,marker='^',color = 'g' ,label = 'buy_point')
        plt.scatter(draw_log.index, draw_log.sell_point/ init_open,marker='^',color = 'r' ,label = 'sell_point')
        plt.legend()
        plt.title('Strategy VS Index')
        plt.savefig('./pic/logVs.jpg')
        plt.show()

        plt.figure(figsize= (10,5))
        plt.plot(log.index, log.capital/capital,label = 'capital')
        plt.title('Strategy')
        plt.savefig('./pic/log.jpg')
        plt.show()













