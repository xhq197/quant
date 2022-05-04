import pandas as pd
import tushare as ts

class GetData:
    @staticmethod
    def get_csv_data(index_name):
        df = pd.read_csv('./data/' + index_name + '.csv', skiprows = 3)
        df.rename({'Date':'DATETIME','MACD':'MACD_MACD','MACD.1':'MACD_DIFF','MACD.2':'MACD_DEA'\
                        ,'KDJ':'KDJ_K','KDJ.1':'KDJ_D','KDJ.2':'KDJ_J'},inplace = True,axis=1)
        return df


    @staticmethod
    def get_csv_data_v1(index_name):
        '''
        数据Version2
        '''
        df = GetData.get_csv_data(index_name)
        plus_names= ['技术指标补充1','技术指标补充2','收盘行情补充','成分分析_指数因子','技术形态']
        for plus_name in plus_names:
            df = df.merge(pd.read_csv('./data/' + index_name + '_'+plus_name + '.csv', skiprows = 3)\
                          ,left_on='DATETIME',right_on='Date',how = 'left')
            df.drop('Date',inplace=True,axis = 1)
        return df

    @staticmethod
    def get_stocks(list_status):
        '''
        #查询当前所有正常上市交易的股票列表
        :param list_status: L上市 D退市 P暂停上市
        :return:
        '''
        # pd.set_option('display.max_rows', 50000)
        # pd.set_option('display.max_columns', 50000)
        # pd.set_option('display.width', 2000)
        token='f3ef4ac4dc04104e0573aa75c29aef70f30837a416baf6cd1a0f8e81'
        ts.set_token(token)

        pro = ts.pro_api()
        data = pro.stock_basic(exchange='', list_status=list_status, fields='ts_code,symbol,name,area,industry,list_date')

        # print(data)
        data.to_csv('./data/trade/all_stocks_'+list_status+'.csv')

class handleData:
    @staticmethod
    def change_flag(index,way_num):
        '''
        way_num = 1:
        1 V 0 & target = 1 的shift+_1个均为1
        way_num = 2:
        -1 V 0 & target = -1 的shift+_1个均为-1
        way_num = 3:
        1 -1  V 0 & target = +-1 的shift+-1个均为+-1
        :param index: 含有flag和feature的df
        :return:
        '''
        if way_num == 1:
            index.loc[index.target == -1, 'target'] = 0
            index.target_shift1 = index.target.shift(1)
            index.target_shift1.fillna(0, inplace=True)
            index.target_shift2 = index.target.shift(-1)
            index.target_shift2.fillna(0, inplace=True)
            index.target += index.target_shift1
            index.target += index.target_shift2
        elif way_num == 2:
            index.loc[index.target == 1, 'target'] = 0
            index.loc[index.target == -1, 'target'] = 1
            index.target_shift1 = index.target.shift(1)
            index.target_shift1.fillna(0, inplace=True)
            index.target_shift2 = index.target.shift(-1)
            index.target_shift2.fillna(0, inplace=True)
            index.target += index.target_shift1
            index.target += index.target_shift2
        elif way_num == 3:
            index.target_shift1 = index.target.shift(1)
            index.target_shift1.fillna(0, inplace=True)
            index.target_shift2 = index.target.shift(-1)
            index.target_shift2.fillna(0, inplace=True)
            index.target += index.target_shift1
            index.target += index.target_shift2
        index.target = index.target.astype('int32')
        return index





