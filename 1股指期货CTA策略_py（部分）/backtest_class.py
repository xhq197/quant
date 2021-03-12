# 打包回测代码
# 未来优化建议：
# 长短期回测代码on_init不用加if判断long、short
# check传入列名

'''
author : xie huiqin
version : backtest
updata_time : 2020/07/23 
'''

from algoqi.backtest import AQ
from algoqi.backtest.models import BacktestConfig
from algoqi.data import D
from algoqi.tsdata.model import DataDeliveryMode, TSDataFormat
import algoqi.data.plotutils as P
import pandas as pd
from ResAssese import ResultAssese
import warnings
warnings.filterwarnings("ignore")

from algoqi.api.default_api import *
import numpy as np
from algoqi.data import wind

from datetime import datetime,timedelta
import re

import json

class backtest:
    """
    短期日内回测，如一个月，return：res.logs 和 res.trades
    """
     
    def bt_short(py_path = './final_5min.py',symbol = 'IC1910.CF',start = '20190923',end = '20191018',N = 5,per_size = 1):

        params_dict = {
            'symbol':symbol,
            'per_size': per_size
        }

        def params_func(*args, **kwargs):
            return {
                'symbol': symbol,
                'per_size': per_size,
                'start':start,
                'end':end,
                'N':N,
                'long_short':'short'
            }

        config = BacktestConfig(sub_config=[])
        config.start_ts = start
        config.end_ts = end
        config.fields = "*"  
        config.split = None
        config.datasource = "future_tick"

        config.init_positions = []
        config.symbols = [symbol + 'E']
        config.param = params_dict
        res = AQ.backtest_local(py_path, config, params_dict=params_func, convert_to_df=True)
#         if save:
#             res.to_csv(save_path)
        if res.is_success:
            print("done")
            
        return res

    
    def evaluation(trades,logs,code ='IC00.CFE',start = "20190102",end ="20191231",html_out = False,html_path = 'fig_html' ):
        """
        评估绘图
        
        return:
        ------------
        res_dict = {
        'pos':,
        'ret':,
        'pos_time':,
        'ResultAssese':计算平均每笔收益、盈亏比、胜率、交易次数、平均持仓时间，输出格式为dataframe,
        }
        fig_dict = {
        'FigTradesSig' : 带交易标记的K线图,
        'FigTradesSig_update' : update后带交易标记的K线图,
        'FigRetPerSize' : 每笔收益柱状图,
        'p_ls' : 累计收益图，不区分long和short【有误】,
        'p_long' : long仓位累计收益图【有误】,
        'p_short' : short仓位累计收益图【有误】
        }
        """
        
        res_dict = {}
        fig_dict = {}
        
        pos = ResultAssese.pos_all(trades)
        ret = ResultAssese.RetPerSize(trades)
        pos_time = ResultAssese.PosTime(trades)
        
        res_dict['pos'] = pos
        res_dict['ret'] = ret
        res_dict['pos_time'] = pos_time

        # 计算平均每笔收益、盈亏比、胜率、交易次数、平均持仓时间，输出格式为dataframe
        res_dict['ResultAssese'] = ResultAssese.res_assess(trades)
        #print(res_dict['ResultAssese'])
        #绘制带交易标记的K线图
        fig_dict['FigTradesSig'] = ResultAssese.FigTradesSig(code,start,end,trades)
        #绘制update后带交易标记的K线图
        fig_dict['FigTradesSig_update'] = ResultAssese.FigTradesSig_update(code,start,end,trades,logs)
        if html_out:       
            # 生成html
            fig_dict['FigTradesSig'].save_file(html_path)
        #绘制每笔收益柱状图
        fig_dict['FigRetPerSize'] = ResultAssese.FigRetPerSize(ret)
#         #绘制累计收益图，不区分long和short【有误】
#         fig_dict['p_ls'] = ResultAssese.FigAccuRet(pos)
#         #绘制long仓位累计收益图【有误】
#         fig_dict['p_long'] = ResultAssese.FigAccuRet_L(pos)
#         #绘制short仓位累计收益图【有误】
#         fig_dict['p_short'] = ResultAssese.FigAccuRet_S(pos)
        ret_df = ResultAssese.RetPerSize_update(trades)
        fig_dict['FigRetPerSize_update'] = ResultAssese.FigRetPerSize_update(ret_df,logs)
        fig_dict['FigAccuRet'] = ResultAssese.FigAccuRet(ret_df)
        return res_dict,fig_dict
    
    def bt_long(py_path = './final_5min.py',code = 'IC00.CFE',start = '20190102',end = '20191231'
                ,N = 5,per_size = 1,save = False,save_path = './final_5min.pkl',save_name = 'final_5min',
               k_min_high_level = 1,k_min_low_level = 1,use_tick_merge = False):
        '''
        return：
        -----------
        trades_df: 交易记录
        logs_df: 日志记录
        
        target
        -----------
        做长期回测，如一年
        
        parameter
        -----------
        py_path：策略文件路径
        code：获取当月合约，统一使用'IC00.CFE'
        start：回测开始时间（必须是交易日）
        end: 回测结束时间
        N: 时间切割策略中，回测使用的K线数据做几次切割。如：N = 5（使用5minK线）代表将5minK线切割5次，生成5套5minK线数据。
        per_size: 单次交易购买的合约数，一般情况下，使用per_size = 1
        save: 是否存储回测过程中交易和日志的中间结果:trades_df,logs_df
        save_path: 交易和日志的中间结果的存储路径
        save_name: 建议使用策略文件名，或者在策略文件名上加一些尾注
        k_min_high_level : （int）在第三买卖点策略中标识计算中枢的K线级别，如k_min_high_level =30 表示计算中枢的高级K线是30min K线
        k_min_low_level :  （int）在第三买卖点策略中标识计算笔的K线级别
        use_tick_merge : use_tick_merge = True，使用tick数据合成K线；use_tick_merge = False，使用平台提供的K线数据。        
        
        '''

        symbol = code               # 回测品种
        beg_date = start             # 回测开始时间,开始时间不能是周末    
        end_date = end            # 回测结束时间

        symbols_list = D.CONT_FUT('IC00.CFE').symbols_during(beg_date,end_date)
        start = [symbols_list[i][1] for i in range(0,len(symbols_list))]
        end = [symbols_list[i][2] for i in range(0,len(symbols_list))]
        code = [symbols_list[i][3][0]+'E' for i in range(0,len(symbols_list))]

        res_trades =[]       # 构造空的dataframe
        res_log = []
        for i in range(0,len(symbols_list)):
            
            if i > 0:j = i-1
            else:j = 0
                
            params_dict = {
                'symbol':code[i],
                'per_size': per_size,
                'start':start[i],
                'latest_end':end[j],
                'first_start':start[0],
                'last_end':end[-1],
                'end':end[i],
                'N':N,
                'long_short':'long',
                'py_name':save_name,
                'k_min_high_level':k_min_high_level,
                'k_min_low_level':k_min_low_level,
                'use_tick_merge':use_tick_merge
                
                }
            def params_func(*args, **kwargs):
                return {
                    'symbol': code[i],
                    'per_size': per_size,
                    'start':start[i],
                    'latest_end':end[j],
                    'first_start':start[0],
                    'last_end':end[-1],
                    'end':end[i],
                    'N':N,
                    'long_short':'long',
                    'py_name':save_name,
                    'k_min_high_level':k_min_high_level,
                    'k_min_low_level':k_min_low_level,
                    'use_tick_merge':use_tick_merge
                    }

            print('\n',start[i],'-',end[i])
            config = BacktestConfig(sub_config=[])
            config.start_ts = start[i] 
            config.end_ts = end[i]
            # config.fields = ["B1", "S1"]
            config.fields = "*"  
            config.split = None
            config.datasource = "future_tick"

            # config.init_positions = [("AU1912", LongShortType.LONG, 0), \\("AU1912", LongShortType.SHORT, 0)]
            config.init_positions = []
            config.symbols = [code[i]]                 #这里是列表，一定要注意数据结构
            config.param = params_dict

            res = AQ.backtest_local(py_path, config, params_dict=params_func, convert_to_df=True)
            res_log.append(res.logs)
            res_trades.append(res.trades)
            #中间存储
            if save:
                trades_df0 = pd.concat(res_trades)
                logs_df0 = pd.concat(res_log)
                try:
                    loc = save_path.rindex('/')
                    
                    save_path_trades = list(save_path)
                    save_path_trades.insert(loc+1, 'trades_')
                    save_path_trades=''.join(save_path_trades)
                    
                    save_path_logs = list(save_path)
                    save_path_logs.insert(loc+1, 'logs_')
                    save_path_logs=''.join(save_path_logs) 
                    
                except Exception as e:
                    raise ValueError(r'Save_path must contain at least one /')
    
                
                trades_df0.to_pickle(save_path_trades)
                logs_df0.to_pickle(save_path_logs)

        trades_df = pd.concat(res_trades)  #输出的是list，要转化为dataframe
        logs_df = pd.concat(res_log)  #输出的是list，要转化为dataframe
        return trades_df,logs_df
    
    def get_IC_date(start = '20190102',end = '20191231'):

        '''
        获取一定时间段内各个期货品种的起止时间
        '''
        beg_date = start
        end_date = end
        symbols_this_month = ['IC00.CFE']
        symbols_next_month = ['IC01.CFE']

        Beg_date=pd.to_datetime(beg_date)-timedelta(days=31)
        End_date=pd.to_datetime(end_date)+timedelta(days=31)
        Beg_date=Beg_date.strftime('%Y%m%d')
        End_date=End_date.strftime('%Y%m%d')

        symbols_this_month = ['IC00.CFE']
        code_IC_this_month = wind.query_wind("SELECT FS_MAPPING_WINDCODE,STARTDATE,ENDDATE FROM wind_filesync.CFUTURESCONTRACTMAPPING\
                                             WHERE S_INFO_WINDCODE = '"  + symbols_this_month[0] +\
                                             "' and STARTDATE >= '" + Beg_date + "' and ENDDATE <= '" + End_date + "'")
        code_IC_this_month=code_IC_this_month.sort_values(by='STARTDATE',ascending=True)
        
        return code_IC_this_month
    
    @staticmethod
    def check(trades,logs):
        #排查开平仓的问题，统计各类交易所占的比例
#         trades = res.trades.copy()
#         logs = res.logs.copy()
        if len(trades.index.get_duplicates()) != 0:
            print('警告：有重复索引!!!')


#         short_logs_df = pd.DataFrame(logs).copy()
#         short_logs_df.rename({'1':'log'},axis = 1,inplace = True)
#         short_logs_df.rename({1:'log'},axis = 1,inplace = True)
#         short_logs_df['logs_shorter'] = short_logs_df['log'].apply(lambda x:x[:-7])
#         count_res = short_logs_df[(short_logs_df['log'] != 'initialize params') & (short_logs_df['log'] != 'stop strategy')]\
#                 .groupby(by = 'logs_shorter').count().copy()
#         count_res['ratio'] = count_res['log']/count_res['log'].sum()*2
        
#         if ('破底CL' in count_res.index) or ('破顶CS' in count_res.index):
#             print('止损次数/总平仓次数 = ',count_res['ratio'][['破底CL','破顶CS']].sum().round(4))
#         else:
#             print('止损次数/总平仓次数 = ',0)

        print('开多头次数是否等于平多头次数：',len(trades[(trades['LS'] == 'LONG') & (trades['open_close'] == 'OPEN') ]) ==\
                        len(trades[(trades['LS'] == 'LONG') & (trades['open_close'] == 'CLOSE') ]))
        print('开空头次数是否等于平空头次数：',len(trades[(trades['LS'] == 'SHORT') & (trades['open_close'] == 'OPEN') ]) ==\
                        len(trades[(trades['LS'] == 'SHORT') & (trades['open_close'] == 'CLOSE') ]))
        def A_in_B(A,B):
            #判断list A 是 list B的一部分
            return not(any([A==B[i:i+len(A)] for i in range(0,len(B)-len(A)+1)]))
        A1 = ['OPEN','OPEN']
        A2 = ['CLOSE','CLOSE']
        B_long = trades[trades['LS'] == 'LONG']['open_close'].to_list()
        B_short = trades[trades['LS'] == 'SHORT']['open_close'].to_list()
        print('是否只有平掉现有的头寸，才能开新的仓位：',
                            all([A_in_B(A1,B_long) 
                            , A_in_B(A2,B_long)
                            ,A_in_B(A1,B_short)
                            ,A_in_B(A2,B_short)]))
        print('***************'*5)

    
    @staticmethod
    def analysis(trades_df,logs_df):
       #计算开平仓次数和各类平仓的盈亏 
#         ret = ResultAssese.RetPerSize_update(trades_df)
#         logs = logs_df.copy()
#         logs.index.name = 'ts'
#         logs.rename({'1':'logs',1:'logs'},axis = 1,inplace = True)
#         ret_logs = pd.concat([ret,logs],axis =1)
#         ret_logs.dropna(inplace = True)
#         ret_logs['logs_shorter'] = ret_logs['logs'].apply(lambda x : x[:-7])
#         ret_logs['logs_classify'] = ret_logs['logs_shorter'].apply(lambda x: '主动收益' if x=='CL' or x == 'CS'\
#                                                                    else '结算收益'if x == 'end_CL' or x == 'end_CS'
#                                                                   else '止损收益')
#         backtest.check(trades_df,logs_df)
#         print('log:次数统计，ratio:次数占比\n')
#         print('***************'*5)
# #         analysis_close = ret_logs.groupby(by = 'logs_shorter')['ret_all'].agg([np.max,np.min,np.std,np.mean,np.median,np.sum])\
# #                     .apply(lambda x: round(x,1))
#         analysis_close = ret_logs.groupby(by = 'logs_shorter')['ret_all'].describe()\
#                     .apply(lambda x: round(x,1))

#         analysis_close.loc['Row_sum'] = analysis_close.apply(lambda x: x.sum())

# #         analysis_close_res = ret_logs.groupby(by = 'logs_classify')['ret_all'].agg([np.max,np.min,np.std,np.mean,np.median,np.sum])\
# #                     .apply(lambda x: round(x,1))
#         analysis_close_res = ret_logs.groupby(by = 'logs_classify')['ret_all'].describe()\
#                     .apply(lambda x: round(x,1))

#         analysis_close_res.loc['Row_sum'] = analysis_close_res.apply(lambda x: x.sum())
#         return analysis_close,analysis_close_res
       #计算开平仓次数和各类平仓的盈亏 
        backtest.check(trades_df,logs_df)
        ret = ResultAssese.RetPerSize_update(trades_df)
        logs = logs_df.copy()
        logs.index.name = 'ts'
        logs.rename({'1':'logs',1:'logs'},axis = 1,inplace = True)
        ret_logs = pd.concat([ret,logs],axis =1)
        ret_logs.dropna(inplace = True)
        ret_logs['logs_shorter'] = ret_logs['logs'].apply(lambda x : x[:-7])
        ret_logs['logs_classify'] = ret_logs['logs_shorter'].apply(lambda x: '主动收益' if x=='CL' or x == 'CS'\
                                                                   else '结算收益'if x == 'end_CL' or x == 'end_CS'
                                                                  else '止损收益')
        def detail_analysis_close(ret_logs,group_name = 'logs_shorter'):
            analysis_close = ret_logs.groupby(by = group_name).agg([np.max,np.min,np.std,np.mean,np.median,np.sum])\
                        .apply(lambda x: round(x,1))
            analysis_close_count = ret_logs.groupby(by = group_name).count()
#             analysis_close_count.name = 'count'
            analysis_close['count'] = analysis_close_count['ret_all']
            analysis_close.loc['Row_sum'] = analysis_close.apply(lambda x: x.sum())
            analysis_close['count_ratio'] = (analysis_close['count']/analysis_close.loc['Row_sum','count'].iloc[0]).round(4)
           
            analysis_close.loc['Row_sum',(['ret_long','ret_short','ret_all'],['mean','std','amin','median','amax'])] = np.nan
            return analysis_close


        def analysis_close_func(ret_logs,group_name = 'logs_shorter',ret_name = 'ret_all'):
            '''
            对ret_all(所有仓位)进行统计分析
            '''
            analysis_close = ret_logs.groupby(by = group_name)[ret_name].describe()\
                        .apply(lambda x: round(x,1))
            analysis_close_sum = ret_logs.groupby(by = group_name)[ret_name].sum()
            analysis_close_sum.name = 'return_sum'
            analysis_close  = pd.concat([analysis_close,analysis_close_sum],axis =1)
            analysis_close.loc['Row_sum'] = analysis_close.apply(lambda x: x.sum())
            analysis_close['count_ratio'] = (analysis_close['count']/analysis_close.loc['Row_sum','count']).round(4)
            analysis_close.loc['Row_sum',['mean','std','min','25%','50%','75%','max']] = np.nan
            analysis_close = analysis_close[['count','count_ratio','min','25%','50%','75%','max','std','mean','return_sum']]
            return analysis_close
#         analysis_close = analysis_close_func(ret_logs,group_name = 'logs_shorter',ret_name = 'ret_all')
        analysis_close= detail_analysis_close(ret_logs)
        analysis_close_res = analysis_close_func(ret_logs,group_name = 'logs_classify',ret_name = 'ret_all')

        return analysis_close,analysis_close_res

class  strategy:
    @staticmethod
    def time_str(df,time_to_str = True,col_name = 'DATETIME',prices_part = False):
        '''
        日内回测跨日使用之前的计算结果，U.update修改dataframe和dict的Timestamp
        time_to_str = True : timestamp->str
        time_to_str = False : str->timestamp
        '''
        if time_to_str:
            # timestamp->str
            if isinstance(df, pd.DataFrame):
#                 if prices_part:
#                     df['parting_time'] = df['parting_time'].apply(lambda x:x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, pd.Timestamp))
#                     df['pen_point_time'] = df['pen_point_time'].apply(lambda x:x.strftime('%Y-%m-%d %H:%M:%S')
#                                                                       if isinstance(x, pd.Timestamp))
                df[col_name] = df[col_name].apply(lambda x:x.strftime('%Y-%m-%d %H:%M:%S'))
                df = json.loads(df.reset_index().to_json())
            elif isinstance(df, dict):
                for key in df:
                    if isinstance(df[key], pd.Timestamp):
                        df[key] = df[key].strftime('%Y-%m-%d %H:%M:%S')
#                     df[key] = json.loads(df[key].to_json())

        else:
            # str->timestamp
            if isinstance(df, pd.DataFrame):
                df[col_name] = df[col_name].apply(lambda x:pd.Timestamp(x))
            elif isinstance(df, dict):
                for key in df:
                    if isinstance(df[key], str):
                        an = re.search('-+', df[key])
                        bn = re.search(':+',df[key])
                        if an and bn:
                            df[key] = pd.Timestamp(df[key])
        return df
    
    
    
    @staticmethod
    def dict_no_nat(series):
        '''
        将接收到的series中的Nat变成None，并以dict形式输出。
        '''
        series = series.fillna('N')
        series_dict = series.to_dict()
        for i in series_dict:
            if series_dict[i] == 'N':
                series_dict[i] = None
        return series_dict
    
    
    
class roll_test:
    
    
    @staticmethod
    def init_handle(trades_df,logs_df):
        #读取csv之后，作进入评估之前的初步运算
        trades_df['datetime'] = trades_df.ts
        trades_df['datetime'] = trades_df['datetime'].apply(lambda x:pd.Timestamp(x))
        trades_df['datetime'] = trades_df['datetime'].apply(lambda x:x.strftime('%Y-%m-%d %H:%M:%S'))
        trades_df.ts = trades_df.ts.apply(lambda x:pd.Timestamp(x))
        trades_df.set_index('ts',inplace = True)

        logs_df['0'] = logs_df['0'].apply(lambda x:pd.Timestamp(x))
        logs_df.set_index(logs_df.columns[0],inplace = True)
        return trades_df,logs_df



    @staticmethod
    def asscess(trades_df,logs_df,return_choice = False):
        long_res_dict,long_fig_dict = backtest.evaluation(trades =trades_df,logs = logs_df,\
                                             start = start,end =end,html_out = False)
        analysis_close,analysis_close_res = backtest.analysis(trades_df,logs_df)
        count_res = backtest.check(trades_df,logs_df,print_choice = False)
        print('\nret_long:多头单笔收益，ret_short:空头单笔收益，ret_all：不区分多空头的单笔收益\n')
        print(analysis_close)
        print('\n 主动收益:CL&CS ,结算收益：end_CL&end_CS,止损收益：破底CL&破底CS\n')
        print(analysis_close_res)
        print('***************'*5)
        print(long_res_dict['ResultAssese'])
        if return_choice:
            #long_res_dict:表格结果 ，long_fig_dict:图像结果，analysis_close：平仓分类结果，analysis_close_res：平仓分类汇总结果，count_res：平仓计数结果
            return long_res_dict,long_fig_dict,analysis_close,analysis_close_res,count_res
        
    @staticmethod   
    def data_cut_asscess(trades_df,logs_df,period = 6):
        '''
        多折回测
        输入长期回测的trades_df 和 logs_df
        
        example
        -----------
        start = '20190102'
        end = '20191231'
        py_path0 = './波动率/vol_base.py'
        save_name0 = 'vol_base'
        period = 6 #6个月为一组
        trades_df = pd.read_csv('./circle/trades_'+save_name+start+'_'+end+'.csv')
        logs_df = pd.read_csv('./circle/logs_'+save_name+start+'_'+end+'.csv')
        trades_df,logs_df = init_handle(trades_df,logs_df)
        cut_asscess_res = data_cut_asscess(trades_df,logs_df,period = period)
        
        '''
        #period：months
        start_ts = trades_df.index[0] - dateutil.relativedelta.relativedelta(hours=8)
        end_ts = trades_df.index[-1] + dateutil.relativedelta.relativedelta(hours=8)
        #n:分组数
        n = (end_ts.month - start_ts.month +1) - period +1
        result_df = pd.DataFrame(columns = ['start','end','交易次数','主动占比','止损占比','结算占比',
                       '单笔主动','单笔止损','单笔结算',
                       '累计主动','累计止损','累计结算',
                                '收益合计','月均收益'])
        #### 暂时修改range(n)
        for i in range(n):
            start = start_ts+dateutil.relativedelta.relativedelta(months=i)
            end = end_ts - dateutil.relativedelta.relativedelta(months=n-1-i)
            trades_df_cut = trades_df[(trades_df.index<= end)&(trades_df.index>= start)]
            logs_df_cut = logs_df[(logs_df.index<= end)&(logs_df.index>= start)]
            print('\n','////////////'*6)
            print('\n','////////////'*6)
            print('第{}组/共{}组：'.format(i+1,n))
            print(start,'_',end)
    #         asscess(trades_df_cut,logs_df_cut)
            long_res_dict,long_fig_dict,analysis_close,analysis_close_res,count_res = asscess(trades_df_cut,logs_df_cut,return_choice =True)
            index_name = '第'+str(i+1)+'组'
            result_df.loc[index_name,'start'] = start.strftime('%Y%m%d')
            result_df.loc[index_name,'end'] = end.strftime('%Y%m%d')
            result_df.loc[index_name,'交易次数'] = long_res_dict['ResultAssese'].loc['total','trades_count']/2
            if ('CL' in count_res.index) or ('CS' in count_res.index):
                result_df.loc[index_name,'主动占比'] = count_res['ratio'][['CL','CS']].sum().round(2)
            else:
                result_df.loc[index_name,'主动占比'] = 0

            if ('破底CL' in count_res.index) or ('破顶CS' in count_res.index):
                result_df.loc[index_name,'止损占比'] = count_res['ratio'][['破底CL','破顶CS']].sum().round(2)
            else:
                result_df.loc[index_name,'止损占比'] = 0

            if ('end_CL' in count_res.index) or ('end_CS' in count_res.index):
                result_df.loc[index_name,'结算占比'] = count_res['ratio'][['end_CL','end_CS']].sum().round(2)
            else:
                result_df.loc[index_name,'结算占比'] = 0
            try:
                result_df.loc[index_name,'单笔主动'] = analysis_close_res.loc['主动收益',('ret_all','mean')].round(1)
            except Exception as e:
                result_df.loc[index_name,'单笔主动'] = np.nan

            try:
                result_df.loc[index_name,'单笔止损'] = analysis_close_res.loc['止损收益',('ret_all','mean')].round(1)
            except Exception as e:
                result_df.loc[index_name,'单笔止损'] = np.nan

            try:
                result_df.loc[index_name,'单笔结算'] = analysis_close_res.loc['结算收益',('ret_all','mean')].round(1)
            except Exception as e:
                result_df.loc[index_name,'单笔止损'] = np.nan

            try:
                result_df.loc[index_name,'累计主动'] = analysis_close_res.loc['主动收益',('ret_all','sum')].round(1)
            except Exception as e:
                result_df.loc[index_name,'累计主动'] = np.nan

            try:
                result_df.loc[index_name,'累计止损'] = analysis_close_res.loc['止损收益',('ret_all','sum')].round(1)
            except Exception as e:
                result_df.loc[index_name,'累计止损'] = np.nan

            try:
                result_df.loc[index_name,'累计结算'] = analysis_close_res.loc['结算收益',('ret_all','sum')].round(1)
            except Exception as e:
                result_df.loc[index_name,'累计结算'] = np.nan



            result_df.loc[index_name,'收益合计'] = analysis_close_res.loc['Row_sum',('ret_all','sum')].round(1)
            result_df.loc[index_name,'月均收益'] = (analysis_close_res.loc['Row_sum',('ret_all','sum')]/(n-1)).round(1)

            df = result_df.copy()
            df.loc['组间标准差'] = df.iloc[:,2:].apply(lambda x: x.std().round(2))
            df.loc['组间均值'] = df.iloc[:-1,2:].apply(lambda x: x.mean()).apply(lambda x:round(x,2))

            #修改输出格式


        return df
    
class classify:
    '''
    对回测结果按主动交易、止损交易、结算交易进行分类统计。
    '''

    def trades_logs_func(trades_df,logs_df):
        '''
        对trades\logs分类之前的预处理，返回值被classify_trades_logs调用。
        '''
        logs_to_df = pd.DataFrame(logs_df)
        logs_to_df['logs_shorter'] = logs_to_df[1].apply(lambda x:x[:-7])
        trades_logs = pd.concat([trades_df,logs_to_df],axis = 1)
        trades_logs = trades_logs[(trades_logs['logs_shorter']!= 'initialize' )& (trades_logs['logs_shorter']!= 'stop s')]
        return trades_logs
    
    def classify_trades_logs_func(trades_logs,classify_name = 'active',
                            classify_dict = {'active':['CS','CL'],'passive':['破底CL','破顶CS'],'end':['end_CS','end_CL']}):

        trades_logs.loc[(trades_logs['logs_shorter'] == classify_dict[classify_name][0]) | (trades_logs['logs_shorter'] == classify_dict[classify_name][1]),'flag'] = 1
        trades_logs['flag_shift'] = trades_logs['flag'].shift(-1)
        trades_logs = trades_logs.fillna({'flag':0,'flag_shift':0})
        trades_logs['flag_sum'] = trades_logs['flag'] + trades_logs['flag_shift']

        classify_trades_logs = trades_logs[trades_logs['flag_sum'] == 1]
        classify_trades_df = classify_trades_logs[['sym','price','qty','LS','open_close']].copy()
        classify_trades_df.index.name = 'ts'
        classify_logs_df = classify_trades_logs[[1]].copy()
        classify_logs_df.index.name = 0
        return classify_trades_df,classify_logs_df
    
    def classify_analysis(trades_df,logs_df,start,end,classify_name = 'active'):
        trades_logs = classify.trades_logs_func(trades_df,logs_df)
        classify_trades_df,classify_logs_df = classify.classify_trades_logs_func(trades_logs,classify_name = classify_name)
        long_res_dict,long_fig_dict = backtest.evaluation(trades =classify_trades_df,logs = classify_logs_df,\
                                                 start = start,end =end)
        return long_res_dict,long_fig_dict
