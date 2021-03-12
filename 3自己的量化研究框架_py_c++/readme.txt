运行顺序

获取数据
daily_crawler.py
basic_crawler.py
finance_report_crawler.py

对daily进行数据调整
daily_fixing.py

每日自动更新数据
sheduled_crawl_task.py

计算pe
pe_computing.py

计算因子、策略文件
boll_factor.py
fractal_factor.py
macd_factor.py
rsi_factor.py
stock_pool_strategy.py

支撑文件
stock_util.py
tusharePro.py
database.py
log.py

猜测回测文件
backtest.py
利用除权因子aufactor调整持仓股的持仓数量。

待解决
#daily_crawler.py
codes不是历史上所有的股票代码，而是某一天的股票代码
#stock_pool_strategy.py
所有本期持仓与上期持仓重合的部分即持仓股票参与平均收益率计算，而上期持仓包含而本期持仓没有的股票，
即本期应该卖出的股票未进入计算收益
夏普比率计算公式有误？
sharpe_ratio = (annual_profit - 4.75) / (profit_std * pow(245, 1 / 2))



