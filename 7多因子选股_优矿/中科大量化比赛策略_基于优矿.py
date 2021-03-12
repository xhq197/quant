
# coding: utf-8

# # tql队：基于IC-IR的多因子策略
# `成员:` 谢慧琴、陈伟、吴晓明 
# `队长账号:` 15991751413
# `联系电话:`15991751413

# ## 1、策略思路
# 在优矿精选因子中选择7个在各自领域信息比率（IR）最大的单因子，如下所示，在空值处理、标准化之后，经IC-IR方式组合得来。
# 
# `领域`	    因子
# `价值`	    现金流市值比（CTOP）
# `动量`	    分析师盈利预测变化趋势 （GREV）
# `成长`	    利润总额增长率 （TotalProfitGrowRate）
# `情绪类`	   120日平均换手率 （VOL120）
# `收益和风险类` 超额流动 （TOBT）
# `分析师类`	   分析师推荐评级 （REC）
# `常用技术指标` 收益相对金额比 （ILLIQUIDITY）
# 

# ## 2、数据准备

# In[ ]:

import pandas as pd
from datetime import datetime
import datetime
import numpy as np
import scipy.stats as st


# #### 2.1 设置股票池

# In[ ]:

universe = DynamicUniverse('000906.ZICN')
begin_date = '20090101'
end_date = '20191231'
trade_date_list = DataAPI.TradeCalGet(exchangeCD=u"XSHG,XSHE", beginDate=begin_date, endDate=end_date, field=u"calendarDate,isOpen,isMonthEnd", pandas="1")
trade_date_list = trade_date_list[trade_date_list['isMonthEnd'] == 1]['calendarDate'].tolist()
#除去trade_date_list中的重复项
#trade_date_list：每月最后一个交易日
trade_date_list= sorted(set(trade_date_list),key=trade_date_list.index)


# In[ ]:

#验证trade_date_list中无重复项
if len(trade_date_list)==12*(2019-2009+1):
    pass
else:
    print("报错：trade_date_list中有重复项！")


# #### 2.1 每个交易日剔除ST股票及上市不足60日的次新股

# In[ ]:

def ST_60new_filter(universe,trade_date):
    """持仓股票剔除ST股票及上市不足60日的次新股
    """
    raw_universe=universe.preview(date=trade_date)
    #ST_stock:月末交易日有ST警告的公司，ST标记，S*ST-公司经营连续三年亏损，退市预警+还没有完成股改;*ST-公司经营连续三年亏损，退市预警;ST-公司经营连续二年亏损，特别处理;SST-公司经营连续二年亏损，特别处理+还没有完成股改。不包括S-还没有完成股改的公司。
    ST_stock=DataAPI.SecSTGet(beginDate=trade_date,endDate=trade_date,secID=raw_universe,ticker=u"",field=u"",pandas="1")
    ST_stock=ST_stock[ST_stock['STflg']!='S'] #[ST_stock['tradeDate'].isin(trade_date_list)]
    #上市日期不足60日的次新股，猜测指的是交易日。
    list_date=DataAPI.EquGet(secID=raw_universe,ticker=u"",equTypeCD=u"",listStatusCD=u"",exchangeCD="",ListSectorCD=u"1",field=u"secID,listDate",pandas="1")
    d_data=DataAPI.MktEqudGet(secID=raw_universe,ticker=u"",tradeDate=u"",beginDate=trade_date,endDate=trade_date,                       isOpen="",field=u"secID,tradeDate",pandas="1") #股票池日行情 放在循环外
    d_list_date=pd.merge(d_data,list_date,on='secID',how='left')
    d_list_date['tradeDate_time']=d_list_date['tradeDate'].apply(lambda x:datetime.datetime.strptime(x, '%Y-%m-%d'))
    d_list_date['listDate_time']=d_list_date['listDate'].fillna('2000-01-01').map(str).apply(lambda x:datetime.datetime.strptime(x, '%Y-%m-%d'))
    d_list_date['trade_date_delta']=d_list_date['tradeDate_time']-d_list_date['listDate_time']
    new_60=d_list_date[d_list_date['trade_date_delta']<datetime.timedelta(days=60/5*7)][d_list_date['trade_date_delta']>=datetime.timedelta(days=0)]   
    ST_60new=pd.merge(ST_stock,new_60,on=['tradeDate','secID'],how='outer')
    current_universe=list(set(raw_universe).difference(set(ST_60new['secID']))) #set(ST_60new[ST_60new['tradeDate']==trade_date]['secID'])
    return current_universe


# In[ ]:

factor_name_list=['secID','tradeDate','CTOP','GREV','TotalProfitGrowRate','VOL120','TOBT','REC','ILLIQUIDITY']


# #### 2.3 获取股票池其他股票的单因子数据 

# In[ ]:

#[耗时:7min]
factor = pd.DataFrame()
for trade_date in trade_date_list:
    current_universe = ST_60new_filter(universe,trade_date)
    current_factor = DataAPI.MktStockFactorsOneDayGet(tradeDate=trade_date, secID=current_universe, field=factor_name_list) #u"secID,tradeDate,CTOP,CFO2EV,GREV,TotalProfitGrowRate,VOL120,TOBT,REC,ILLIQUIDITY"
    factor = factor.append(current_factor)


# #### 2.4 获取原始因子表factor

# In[ ]:

factor=factor.drop_duplicates().sort_values(by=['secID','tradeDate'])
#ST_60new_filter.csv':原始因子表
#factor.to_csv('ST_60new_filter.csv')
#factor:原始因子表
factor


# In[ ]:

# factor=pd.read_csv('ST_60new_filter.csv')
# factor=factor.drop(['Unnamed: 0'],axis=1)
# factor


# #### 2.5 获取行情信息

# In[ ]:

month_return = DataAPI.MktEqumAdjGet(beginDate=begin_date, endDate=end_date, field='endDate,secID,chgPct')
month_return = month_return.pivot(index='endDate', columns='secID', values='chgPct')
forward_1m_ret = month_return.shift(-1).loc[:, factor.secID.unique()]


# In[ ]:

month_return


# ## 3、因子处理
# - 空值处理
# - 标准化
# 

# #### 3.1 空值处理：用行业均值代替空值

# In[ ]:

# 第一步，拿到股票对应的行业，以申万一级行业为例
sw_map_frame = DataAPI.EquIndustryGet(industryVersionCD=u"010303", industry=u"", secID=u"", ticker=u"", intoDate=u"",field=[u'secID', 'secShortName', 'industry', 'intoDate', 'outDate', 'industryName1','isNew'], pandas="1")
sw_map_frame = sw_map_frame[sw_map_frame.isNew == 1]

print sw_map_frame.head().to_html()

# 第二步，根据股票代码，将行业名称和因子值进行合并
factor_frame = factor.merge(sw_map_frame[['secID','industryName1']], on=['secID'], how='left')
print u'因子值合并行业之后的dataframe:\n'
print factor_frame.head().to_html()

# 第三步，得到各个行业的因子均值
mean_factor_indust = factor_frame.groupby(['industryName1','tradeDate'])[factor_name_list].mean().reset_index()
print u'每天，每个行业的均值为：\n'
for fc1 in factor_name_list[2:]:
    mean_factor_indust.rename(columns={fc1:fc1+"_mean"}, inplace=True)
print mean_factor_indust.head().to_html()

# 第四步，再将行业均值合并到因子的dataframe中
factor_frame1 = factor_frame.merge(mean_factor_indust,on=['tradeDate', 'industryName1'], how='left')
print u'合并行业均值之后的dataframe:\n'
print factor_frame1.head().to_html()

# 第五步，填充空值
for fc2 in factor_name_list[2:]:
    factor_frame1[fc2].fillna(factor_frame1[fc2+'_mean'], inplace=True) #用同行某列的值填充nan
factor_frame1=factor_frame1[factor_name_list+['industryName1']] #注意看结果
print u'空值填充之后的dataframe:factor_frame1\n'
print factor_frame1.head().to_html()


# #### 3.2 标准化

# In[ ]:

factor_frame21=factor_frame1.set_index('secID')
factor_frame21[factor_name_list[2:]]=factor_frame21[factor_name_list[2:]].apply(lambda x:standardize(x))
factor_frame3=factor_frame21.reset_index()


# ## 4、IC_IR加权合成因子
# 取因子过去一段时间的IC均值除以标准差作为当期因子$f_{i}$的权重，即权重向量：
# $$V = (IR_{f_{1}}, IR_{f_{1}}, …, IR_{f_{m}})$$
# 
# `优点`：考虑了因子有效性的差异，稳定性	

# In[ ]:

processed_factor=factor_frame3.copy()
processed_factor.drop_duplicates(subset=['secID','tradeDate'],inplace=True)


# In[ ]:

#验证原始因子表和处理后的因子表行数是否相同
if len(processed_factor)==len(factor):
    pass
    #processed_factor.to_csv('processed_factor.csv')
    #processed_factor=pd.read_csv('processed_factor.csv')
else:
    print('报错：原始因子表和处理后的因子表行数不相同，请继续处理processed_factor。')


# #### 4.1 获得各个单因子的数据透视表

# In[ ]:

#processed_factor:经过数据预处理之后的因子表
#CTOP、CFO2EV等：各个单因子的数据透视表
CTOP = processed_factor.pivot(index='tradeDate', columns='secID', values='CTOP')
#CFO2EV = processed_factor.pivot(index='tradeDate', columns='secID', values='CFO2EV')
GREV = processed_factor.pivot(index='tradeDate', columns='secID', values='GREV')
TotalProfitGrowRate = processed_factor.pivot(index='tradeDate', columns='secID', values='TotalProfitGrowRate')
VOL120 = processed_factor.pivot(index='tradeDate', columns='secID', values='VOL120')
TOBT = processed_factor.pivot(index='tradeDate', columns='secID', values='TOBT')
REC = processed_factor.pivot(index='tradeDate', columns='secID', values='REC')
ILLIQUIDITY = processed_factor.pivot(index='tradeDate', columns='secID', values='ILLIQUIDITY')

#processed_factor_dict = {'CTOP': CTOP, 'CFO2EV': CFO2EV, 'GREV': GREV, 'TotalProfitGrowRate': TotalProfitGrowRate, 'VOL120': VOL120, 'TOBT': TOBT, 'REC': REC, 'ILLIQUIDITY': ILLIQUIDITY}


# In[ ]:

def get_rank_ic(factor, forward_return):
    """
    计算因子的信息系数
    输入：
        factor:DataFrame，index为日期，columns为股票代码，value为因子值
        forward_return:DataFrame，index为日期，columns为股票代码，value为下一期的股票收益率
    返回：
        DataFrame:index为日期，columns为IC，IC t检验的pvalue
    注意：factor与forward_return的index及columns应保持一致
    """
    common_index = factor.index.intersection(forward_return.index)
    ic_data = pd.DataFrame(index=common_index, columns=['IC','pValue'])

    # 计算相关系数
    for dt in ic_data.index:
        tmp_factor = factor.ix[dt]
        tmp_ret = forward_return.ix[dt]
        cor = pd.DataFrame(tmp_factor)
        ret = pd.DataFrame(tmp_ret)
        cor.columns = ['factor']
        ret.columns = ['ret']
        cor['ret'] = ret['ret']
        cor = cor[~pd.isnull(cor['factor'])][~pd.isnull(cor['ret'])]
        if len(cor) < 5:
            continue

        ic, p_value = st.spearmanr(cor['factor'], cor['ret'])   # 计算秩相关系数RankIC
        ic_data['IC'][dt] = ic
        ic_data['pValue'][dt] = p_value
    return ic_data


# #### 4.2 计算各个单因子的IC

# In[ ]:

CTOP_ic = get_rank_ic(CTOP, forward_1m_ret).shift(1)
#CFO2EV_ic = get_rank_ic(CFO2EV, forward_1m_ret).shift(1)
GREV_ic = get_rank_ic(GREV, forward_1m_ret).shift(1)
TotalProfitGrowRate_ic = get_rank_ic(TotalProfitGrowRate, forward_1m_ret).shift(1)
VOL120_ic = get_rank_ic(VOL120, forward_1m_ret).shift(1)
TOBT_ic = get_rank_ic(TOBT, forward_1m_ret).shift(1)
REC_ic = get_rank_ic(REC, forward_1m_ret).shift(1)
ILLIQUIDITY_ic = get_rank_ic(ILLIQUIDITY, forward_1m_ret).shift(1)


# #### 4.3 计算滚动的12个月的单因子IC均值/IC标准差

# In[ ]:

CTOP_rolling_ic = CTOP_ic.rolling(12).mean()/CTOP_ic.rolling(12).std()
#CFO2EV_rolling_ic = CFO2EV_ic.rolling(12).mean()/CFO2EV_ic.rolling(12).std()
GREV_rolling_ic = GREV_ic.rolling(12).mean()/GREV_ic.rolling(12).std()
TotalProfitGrowRate_rolling_ic = TotalProfitGrowRate_ic.rolling(12).mean()/TotalProfitGrowRate_ic.rolling(12).std()
VOL120_rolling_ic = VOL120_ic.rolling(12).mean()/VOL120_ic.rolling(12).std()
TOBT_rolling_ic = TOBT_ic.rolling(12).mean()/TOBT_ic.rolling(12).std()
REC_rolling_ic = REC_ic.rolling(12).mean()/REC_ic.rolling(12).std()
ILLIQUIDITY_rolling_ic = ILLIQUIDITY_ic.rolling(12).mean()/ILLIQUIDITY_ic.rolling(12).std()


# #### 4.4 使用计算每期使用IC加权的因子权重,然后进行因子的合成

# In[ ]:

all_rolling_ic_df = pd.concat((CTOP_rolling_ic['IC'], GREV_rolling_ic['IC'], TotalProfitGrowRate_rolling_ic['IC'], VOL120_rolling_ic['IC'],TOBT_rolling_ic['IC'],REC_rolling_ic['IC'],ILLIQUIDITY_rolling_ic['IC']), axis=1)
all_rolling_ic_df.columns = factor_name_list[2:]
factor_weight = all_rolling_ic_df.divide(all_rolling_ic_df.abs().sum(axis=1), axis=0)
final_factor = CTOP.multiply(factor_weight['CTOP'], axis=0) +GREV.multiply(factor_weight['GREV'], axis=0) + TotalProfitGrowRate.multiply(factor_weight['TotalProfitGrowRate'], axis=0) +VOL120.multiply(factor_weight['VOL120'], axis=0)+TOBT.multiply(factor_weight['TOBT'], axis=0)+REC.multiply(factor_weight['REC'], axis=0)+ILLIQUIDITY.multiply(factor_weight['ILLIQUIDITY'], axis=0)


# #### 4.5 验证组合因子在每期，对投资域（中证800）股票的覆盖度>80%（有非空值的比例>80%）

# In[ ]:

proof_factor=final_factor.copy()
if (proof_factor.count(axis=1)/800>=0.8).iloc[12:].all():
    pass
else:
    print('报错：组合因子在每期，对投资域（中证800）股票的覆盖度<80%。')


# ## 5、最终结果

# #### 5.1 combined_factor：最终合成的组合因子数据（透视表形式）

# In[ ]:

combined_factor=final_factor.iloc[12:,:]


# In[ ]:

#combined_factor.to_csv('combined_factor.csv')


# #### 5.2 upload_factor:可直接上传作为私有因子的组合因子表

# In[ ]:

upload_factor=combined_factor.copy()
upload_factor.reset_index(inplace=True)
upload_factor['tradeDate']=upload_factor['tradeDate'].apply(lambda x:x.replace('-',''))
upload_factor.set_index('tradeDate',inplace=True)


# In[ ]:

# upload_factor.to_csv('upload_factor.csv')


# #### 5.3 combined_factor2:最终合成的组合因子数据，可直接导入回测策略

# In[ ]:

combined_factor1=combined_factor.copy()
combined_factor2=pd.DataFrame(combined_factor1.unstack())
combined_factor2.reset_index(inplace=True)
combined_factor2.rename(columns={0:'factor'},inplace=True)
combined_factor2.dropna(inplace=True)
combined_factor2.set_index('secID',inplace=True)
combined_factor2['factor']=winsorize(combined_factor2['factor'], win_type='NormDistDraw', n_draw=5)  # 去极值


# In[ ]:

# combined_factor2.to_csv('combined_factor2.csv')


# ## 6、回测

# In[ ]:

import pandas as pd, numpy as np
from quartz_extensions.SignalAnalysis.tears import analyse_return, analyse_monthly_return, analyse_IC, analyse_construction, analyse_general


# In[ ]:

signal_df=combined_factor2.copy()
signal_df.reset_index(inplace=True)
signal_df.rename(columns={'tradeDate':'date','secID':'ticker','factor':'value'},inplace=True)
signal_df['ticker']=signal_df['ticker'].apply(lambda x:x.split('.')[0])
signal_df['date']=signal_df['date'].apply(lambda x:x.replace('-',''))


# #### 6.1 信号的基本描述

# In[ ]:

date_list = sorted(signal_df['date'].unique())
start_date = date_list[0]
end_date = date_list[-1]
signal_discrip = analyse_general(factor_value_frame=signal_df, start_date=start_date, end_date=end_date, universe='ZZ800', frequency='month')


# #### 6.2 信号的IC相关测试

# In[ ]:

signal_ic = analyse_IC(factor_value_frame=signal_df, start_date=start_date, end_date=end_date, frequency='month', corr_method='spearman', quantile_num=10, universe='ZZ800', benchmark='ZZ800', decay_list=[1, 3, 6, 9])


# #### 6.3 信号的分组测试

# In[ ]:

signal_return = analyse_return(factor_value_frame=signal_df, start_date=date_list[0], end_date=date_list[-1], frequency='month',  quantile_num=5, weight_type='equal', universe='ZZ800', benchmark='ZZ800', init_cash=100000000.0, decay_list=[1, 2, 3, 4])


# #### 6.4 信号的月度表现分析

# In[ ]:

# 月度分析
signal_monthly = analyse_monthly_return(factor_value_frame=signal_df, start_date=start_date, end_date=end_date, frequency='month', quantile_num=10, universe='ZZ800', benchmark='ZZ800')


# ## 7、参考文献
# ---
# [1] 吴先兴.半衰IC加权在多因子选股当中的应用[R].2017.07.22
# [2] 理查德C.格林诺德，雷诺德N.卡恩.主动投资组合管理[M].北京：机械工业出版社，2014:341-346

# ## 附加回测

# In[ ]:

factor_data = combined_factor2[['secID', 'tradeDate', 'factor']]
factor_data = factor_data.set_index('tradeDate', drop=True)
#factor_data.dropna(inplace=True)
#q_dates:tradeDate列表
q_dates = factor_data.index.values


# In[ ]:

start = '2010-01-01'                       # 回测起始时间
end = '2019-12-31'                         # 回测结束时间
benchmark = '000906.ZICN'                        # 策略参考标准
universe = DynamicUniverse('000906.ZICN')           # 证券池，支持股票和基金
capital_base = 100000000                     # 起始资金
freq = 'd'                              
refresh_rate = Monthly(1)  #调仓周期，每个月第一天调仓，基于每个月月末交易日因子值调仓  # 执行handle_data的时间间隔
commission = Commission(buycost=0.0002, sellcost=0.0003, unit='perValue')    #设置手续费 买入万二，卖出万三
# 配置账户信息，支持多资产多账户
accounts = {
    'fantasy_account': AccountConfig(account_type='security', capital_base=10000000)
}
  
def initialize(context):                   # 初始化虚拟账户状态
    pass

def handle_data(context):                  # 每个交易日的买入卖出指令
    account = context.get_account('fantasy_account') #之前account关联
    current_universe = context.get_universe('stock', exclude_halt=True) #获取未停牌的股票池，与之前universe联系
    pre_date = context.previous_date.strftime("%Y-%m-%d")
    if pre_date not in q_dates:            
        return

    # 拿取调仓日前一个交易日的因子，并按照相应分位选择股票
    q = factor_data.ix[pre_date].dropna() #ix可能要改成loc[pre_date,:]
    q = q.set_index('secID', drop=True)
    q = q.ix[current_universe]
    q.dropna(inplace=True)
    #q_min = q['factor'].quantile(0.2)
    q_max = q['factor'].quantile(0.8)
    my_univ = q[q['factor']>=q_max].index.values
    #sell_list=q[q['factor']<=q_min].index.values
    # 交易部分
    positions = account.get_positions() #获取所有账户持仓
    sell_list = [stk for stk in positions if stk not in my_univ]
    for stk in sell_list:
        account.order_to(stk,0)

    # 在目标股票池中的，等权买入
    for stk in my_univ:
        account.order_pct_to(stk, 1.0/len(my_univ))

