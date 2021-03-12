#使用方式all计算三买


import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")
import traceback

from csMarketTiming import MeanReversion
from ResAsseseNoFig import ResultAssese
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows',None)
pd.set_option('display.width', 1000)

def calculateSignal_all(prices_low_level, prices_high_level):
    #### 2.1形成高级k线的中枢

    prices_con_high_level = MeanReversion.contain_treat(prices_high_level, date_col='DATETIME', keep='last',
                                                        col_move=None)

    part_high_level = MeanReversion.part_old(prices_con_high_level)

    trend_prices_high_level = MeanReversion.pen_point_prices(part_high_level, False)  # 默认是False

    pivot_high_level = MeanReversion.pivot_all(trend_prices_high_level, trend_col='pen_point',
                                               accessible_time_col='pen_point_time')

    #### 2.2形成低级k线的笔

    prices_con_low_level = MeanReversion.contain_treat(prices_low_level, date_col='DATETIME', keep='last',
                                                       col_move=None)

    part_low_level = MeanReversion.part_old(prices_con_low_level)


    trend_prices_low_level = MeanReversion.pen_point_prices(part_low_level, False)  # 默认是False

    ####  2.3 高级中枢+ 低级笔 = 三买
    trading_point = MeanReversion.trading_point_all_level_3(pivot_high_level, trend_prices_low_level)
    return trend_prices_low_level, pivot_high_level, trading_point

def keepFirst(l:'list') -> list:
    lastI = None
    newL = []
    for i in l:
        if i == lastI:
            newL.append('00')
        else:
            newL.append(i)
        lastI = i
    return newL




def xhqPayout0916(data,usePen):
    data.DATETIME = pd.to_datetime(data.DATETIME)
    tkr = 'weights'
    idx = data['DATETIME'].drop_duplicates().to_list()
    rows, cols = len(idx), 1
    weights = pd.DataFrame(np.zeros((rows, cols)),index=idx, columns=[tkr])

    # calculate signal for each equity

    equity_price = data.copy()
    try:
        if len(equity_price) >=1:
            prices = prices_high_level = equity_price.dropna()
            trend_prices_low_level0, pivot_high_level0, trading_point0 = calculateSignal_all(prices, prices_high_level)

            if usePen != 'true':
                if len(trading_point0) >= 1:
                    trading_point = trading_point0.copy()
                    trading_point.dropna(inplace=True)
                    trading_point['Error:trading_point_time'] = trading_point['trading_point_time'].astype(str)
                    trading_point.set_index('trading_point_time', inplace=True)
                    weights_three_point = pd.merge(weights, trading_point['trading_point'], left_index=True,
                                                   right_index=True, how='left')
                    weights[tkr] = weights_three_point['trading_point']
                    weights[tkr] =  - weights[tkr]/3





                else:

                    print(f'Error: 无第三买卖点信号！')
                    return
            else:
                if len(trend_prices_low_level0) >= 1:
                    trend_prices_low_level = trend_prices_low_level0.copy()
                    trend_prices_low_level.set_index('pen_point_time', inplace=True)
                    weights_three_point = pd.merge(weights, trend_prices_low_level['pen_point'], left_index=True,
                                                   right_index=True, how='left')
                    weights[tkr] = weights_three_point['pen_point']


                else:
                    print(f'Error: 无笔信号！')
                    return
            weights = weights[(weights[tkr] == 1) | (weights[tkr] == -1)]
            keepList = keepFirst(weights[tkr].to_list())
            keepList = [False if i == '00' else True for i in keepList]
            print(weights[tkr].to_list())
            print(keepList)
            print(weights)
            weights = weights[keepList]

        else:
            print(f'Error: 无数据输入！')
            return
    except Exception as e:
        print('Error:计算信号出错！')
        traceback.print_exc()
    weights = weights.dropna()
    close = data[['DATETIME','close']].set_index('DATETIME')

    close.index.name = None
    weights_close = weights.merge(close, left_index=True, right_index=True, how='left')
    weights_close.rename({'close':'price'},axis=1,inplace=True)
    weights_close.index.name = 'ts'
    return trend_prices_low_level0, pivot_high_level0, trading_point0,weights_close

def calTradesDf(weights_close):
    #-1 买入 1 卖出
    df = weights_close
    if len(df) < 2:
        return None
    if len(df) % 2 != 0:
        if df.iloc[0,0] == 1: df = df.drop(df.index[0])
        else: df = df.drop(df.index[-1])
    df['LS'] = 'LONG'
    df['qty'] = 1
    df['open_close'] = np.where(df.weights == -1,'OPEN','CLOSE')
    print(df)
    return df

def calTable(df,resultPath):
    resAssess = ResultAssese.res_assess(df)
    resAssess.average_pos_time = resAssess.average_pos_time.apply(lambda x:str(x))
    resAssess.iloc[:,:-1] = resAssess.iloc[:,:-1].apply(lambda x:round(x,2))
    resAssess.fillna(0,inplace=True)
    retPerSize = ResultAssese.RetPerSize_update(df)
    retPerSize = retPerSize.apply(lambda x:round(x,2))
    retPerSize.index.name = 'DATETIME'
    retPerSize.reset_index(inplace = True)

    # retPerSize.DATETIME = retPerSize.DATETIME.apply(lambda x:x.strftime('%Y-%m-%d %H:%M:%S'))
    retPerSize = retPerSize.dropna(how = 'any')

    # print('$\n',retPerSize,'\n$\n',resAssess,'\n$')
    retPerSize.to_csv(resultPath+ '\\retPerDict.csv',index = False,header = False)
    resAssess.to_csv(resultPath+ '\\ResultAsseseDict.csv',index = False,header = False)



def calSignal(kline_df,trend_prices_low_level0, pivot_high_level0,trading_point0,resultPath):
    '''
    calSignal 将交易信号变成可以绘图的信号

    '''
    #### 2.1形成高级k线的中枢

    pivot = pivot_high_level0.copy()
    pivot['pivot_end'] = pivot['pivot_end'].fillna(method='backfill')
    pivot.dropna(subset=['zd', 'zg'], how='any', inplace=True)
    pivot.drop_duplicates(inplace=True)

    pivot.reset_index(drop=True, inplace=True)
    pivot_prices_sigle = pivot.drop_duplicates(subset=['pivot_start', 'pivot_end'], keep='last')

    # #取部分使用tick合成的K线数据
    pivot_prices = kline_df.copy()
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
    pivot_high_level = pivot_prices

    #### 2.2形成低级k线的笔

    trend_prices_low_level = trend_prices_low_level0

    ####  2.3 高级中枢+ 低级笔 = 三买
    if len(trading_point0) >= 1:
        trading_point = trading_point0.drop_duplicates(subset=['DATETIME']).copy()
        trading_point = trading_point[(trading_point['trading_point'] == 3) | \
                                      (trading_point['trading_point'] == -3)]

        # trading_point['DATETIME'] = trading_point['DATETIME'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))
        trading_point['trading_point_time'] = trading_point['trading_point_time'].apply(
            lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))
        tradingPointRes = trading_point[['DATETIME', 'trading_point', 'trading_point_time']].dropna(how='any')
    else:
        tradingPointRes = pd.DataFrame()

    ## 3 改成Csharp可读类型,Timestamp to str ,print df

    pivot_high_level.dropna(inplace=True, how='any')
    pivotRes = pivot_high_level
    # trend_prices_low_level['DATETIME'] = trend_prices_low_level['DATETIME'].apply(
    #     lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))
    # trend_prices_low_level['pen_point_time'] = trend_prices_low_level['pen_point_time'].apply(
    #     lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))
    trendRes = trend_prices_low_level[['DATETIME', 'pen_point', 'pen_point_time', 'prices']].dropna(
        how='any')

    # print(pivotRes,'\n$\n',trendRes,'\n$\n',tradingPointRes,'\n$')
    pivotRes.to_csv( resultPath + '\\pivotDict.csv',index=False,header = False)
    trendRes.to_csv( resultPath +'\\trendDict.csv',index=False,header = False)
    tradingPointRes.to_csv(resultPath + '\\tradingPointDict.csv',index=False,header = False)

    # return pivotRes, trendRes, tradingPointRes





def makeCsv(asset = 'AAPL.US Equity'):
    #获取数据
    raw_px = pd.read_csv('D:/pyProject/UBS/data/stocks_price.csv')
    raw_px = raw_px[raw_px.asset == asset]
    raw_px.rename({'date':'DATETIME','open_price': 'open', 'high_price': 'high',
                       'low_price': 'low', 'close_price': 'close'}, axis=1,inplace=True)
    raw_px.drop('asset',axis = 1,inplace=True)
    raw_px.DATETIME = raw_px.DATETIME.apply(lambda x:pd.Timestamp(x))
    saveName = asset.split('.')[0]
    raw_px.to_csv(f'../data/{saveName}.csv',index = False)


def runMain(filePath ,usePen,resultPath):
    '''

    :param filePath: r'D:\pyProject\DF\data\AAPL.csv'
    :param usePen: 'true' or 'false'
    :return: -
    '''
    try:
        raw_px = pd.read_csv(filePath)
        raw_px.sort_values('DATETIME',inplace=True)
        raw_px[['DATETIME','open','high','low','close']].to_csv(resultPath + '\\klineDict.csv',header=False,index=False)
        res = xhqPayout0916(raw_px, usePen)
        if res is not None:
            trend_prices_low_level, pivot_high_level, trading_point, weights_close = res
            tradesDf = calTradesDf(weights_close)
            calTable(tradesDf,resultPath)
            calSignal(raw_px, trend_prices_low_level, pivot_high_level, trading_point,resultPath)
    except Exception as e:
        print('Error:运行出错！')
        traceback.print_exc()

#
# if __name__ == '__main__':
# #     # filePath = r'D:\pyProject\DF\data\AAPL.csv'
# # #     # raw_px = pd.read_csv(filePath)
# # #     # raw_px = raw_px.iloc[:300,:]
# # #     # res = xhqPayout0916(raw_px,'true')
# # #     # if res is not None:
# # #     #     trend_prices_low_level, pivot_high_level, trading_point,weights_close = res
# # #     #     tradesDf = calTradesDf(weights_close)
# # #     #     calTable(tradesDf)
# # #     #     calSignal(raw_px,trend_prices_low_level, pivot_high_level, trading_point)
#     runMain(r'D:\pyProject\DF\data\A.csv','true','../data')
