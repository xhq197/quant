from DATA import GetData
from csMarketTiming import MeanReversion
import numpy as np
class AddFlag:
    @staticmethod
    def get_part_pen_flag(index_data):
        '''
        输入：指数初始数据，包含DATETIME、open、high、low、close
        输出：包含parting、pen_point、flag的df，其中flag是pen向前移动一位的series。
        保存含有特征和flag标签数据。
        注意：分型中2和-2的标记表示更典型的顶底分型,由于是中间结果，不作区分。
        '''
        # index_data = GetData.get_csv_data(index_name)  #.iloc[-1000:, :]  # 注意！！ 只取了部分
        contain = MeanReversion.contain_treat(index_data.iloc[:, :5], date_col='DATETIME', keep='last',
                                              col_move=None)
        part_pen = MeanReversion.part_old(contain)


        index_flag = index_data.merge(part_pen[['DATETIME', 'parting', 'pen_point']],on = 'DATETIME',how = 'left' )
        index_flag.pen_point.fillna(0,inplace = True)
        index_flag.loc[(index_flag['pen_point'] != 1 )& (index_flag['pen_point'] != -1),'pen_point'] = np.nan
        # 注意：分型中2和-2的标记表示更典型的顶底分型,由于是中间结果，不进行探索。
        # 创建含有特征和flag标签的df，今日是否为正负拐点的标签标在昨天的数据上。
        index_flag['flag'] = index_flag.pen_point.shift(-1)
        return  index_flag
