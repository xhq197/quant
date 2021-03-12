# -*- coding: utf-8 -*-
# @Time     : 2020/07/23 13:43
# @Author   ：Li Wenting
# @File     : StatAnalysis.py
# @Software : PyCharm


import numpy as np
import pandas as pd
from numpy import inf

class SignalAnalysis:
    def signal_stat(logs_df):
        '''
        在logs中，记录开仓信号，以日为单位保存在一个list中，以dict的形式打印出来；
        on_stop中的logs会在下一个交易日的开始打印出来，因此会之后一个交易日
        '''
        logs_df.rename(columns = {'1':'event'},inplace = True)
        logs_df['DATETIME'] = pd.to_datetime(logs_df.index).strftime('%Y-%m-%d %H:%M:%S')
        export = []
        for datetime in logs_df['DATETIME'].iloc[1:]:
            if datetime[-8:] == '00:00:00':
                # 这一时刻会有三个输出结果，因此后面需要删掉重复的内容
                export.append(logs_df[logs_df['DATETIME'] == datetime].iloc[1:2])
        export_df = pd.concat(export)
        export_df = export_df.drop_duplicates()
        signal =[eval(x) for x in export_df['event'].values]      #eval去掉字符串，退回到原先的形式
        signal_list = []
        for i in range(0,len(signal)):
            signal_list.append(pd.DataFrame(signal[i]))
        signal_df = pd.concat(signal_list)
        signal_df.set_index(['DATETIME'],inplace = True)
        return signal_df