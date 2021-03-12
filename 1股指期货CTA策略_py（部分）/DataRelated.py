from algoqi.data import D, plotutils
D.switch_zxzx_client(access_key='e7e2de63f95674632824ed6b2be8dd1f', secret_key='d43ca617fe7048e4ccfb158dde8e1c32')
D.load()
import pandas as pd
import numpy as np

class ContFutureSymbolFilter(D.FutContContractFilter):
    '''
    当月合约筛选器
    examle：
    ---------
    symbols=ContFutureSymbolFilter(code)
    '''
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
               
class DataProcess:
    
    @staticmethod
    def get_lab_kline(start = '20190102',end = '20191231',k_min_high_level = 1,code = 'IC00.CFE'):
        '''
        获取lab平台上的股指期货K_line数据
        example：
        ---------
        prices = DataProcess.get_lab_kline(start = '20190102',end = '20191231',k_min_high_level = 1,code = 'IC00.CFE')

        '''

        data = D.query_tsdata(datasource=f'future_kline_{k_min_high_level}min', symbols=ContFutureSymbolFilter(code), fields='*', start=start, end=end)
        prices_list = []
        for df in data:
    #             #xhq modify
    #             df.index = pd.Series(df.index).shift(-1)
    #             df = df.iloc[:-1,:]
    #             ###
            prices_list.append(df)
        prices_df = pd.concat(prices_list)

        prices = prices_df[['Symbol', 'open', 'high', 'low', 'close']]
        prices.reset_index(inplace=True)
        prices = prices.rename(columns={'index':'DATETIME', 'Symbol': 'code'}) 

        return prices