from INFLECTION import AddFlag
from VIS import ReversePointVis
from DATA import GetData
import pandas as pd
index_name = 'sz50'

index_data = GetData.get_csv_data_v1(index_name)
index_flag = AddFlag.get_part_pen_flag(index_data)
index_flag.iloc[:,[i for i in range(len(index_flag.columns)) if i < len(index_flag.columns) -3 \
    or i == len(index_flag.columns) - 1]] \
    .to_csv('./data/'+ index_name +'_flag.csv')


ReversePointVis.short_vis(index_flag.iloc[:50,:],index_name)
ReversePointVis.long_vis(index_flag.iloc[-500:,:],index_name)















