import pandas as pd
import numpy as np
import mplfinance as mpf
import matplotlib.pyplot as plt
from datetime import date




class ReversePointVis:
    @staticmethod
    def short_vis(index_df,index_name,save_path = './pic/short_vis.jpg'):
        '''
        输入50个交易日左右的数据
        输出K线图 + 分型 + 笔（拐点）
        '''
        ### K线、分型、笔的可视化

        draw_df = index_df[['DATETIME', 'open', 'high', 'low', 'close', 'parting', 'pen_point']].copy()


        ## 生成part和pen的标注点
        def part_pen_up_func(parting, high):
            if parting == 1 or parting == 2:
                return high + 5
            else:
                return np.nan

        def part_pen_down_func(parting, low):
            if parting == -1 or parting ==  -2:
                return low - 5
            else:
                return np.nan

        # draw_part为分型part的标记高度，part_pen为笔pen的标记高度。
        draw_df['draw_part_up'] = draw_df.apply(lambda row: part_pen_up_func(row['parting'], row['high']), axis=1)
        draw_df['draw_part_down'] = draw_df.apply(lambda row: part_pen_down_func(row['parting'], row['low']), axis=1)
        draw_df['draw_pen_up'] = draw_df.apply(lambda row: part_pen_up_func(row['pen_point'], row['high']), axis=1)
        draw_df['draw_pen_down'] = draw_df.apply(lambda row: part_pen_down_func(row['pen_point'], row['low']), axis=1)

        add_plot = [
            mpf.make_addplot(draw_df.draw_part_up, scatter=True, color='r', marker='^', markersize=10),
            mpf.make_addplot(draw_df.draw_part_down, scatter=True, color='g', marker='^', markersize=10),
            mpf.make_addplot(draw_df.draw_pen_up, scatter=True, color='r', marker='*', markersize=50),
            mpf.make_addplot(draw_df.draw_pen_down, scatter=True, color='g', marker='*', markersize=50)
        ]




        ## 用原始高开低收数据生成k线
        # # 蜡烛图中只需要high、low的信息。
        draw_df['DATETIME'] = pd.to_datetime(draw_df['DATETIME'], format='%Y-%m-%d')
        draw_df.set_index('DATETIME', inplace=True)
        # draw_df.rename({'open': 'open1', 'close': 'close1'}, axis=1, inplace=True)
        # draw_df.rename({'high': 'open', 'low': 'close'}, axis=1, inplace=True)
        # draw_df.rename({'open1': 'high', 'close1': 'low'}, axis=1, inplace=True)

        ## 用mplfinance包进行绘图，k线 + 分型和笔的标记点。

        # 调用make_marketcolors函数，定义K线颜色
        mc = mpf.make_marketcolors(
            up="red",  # 上涨K线的颜色
            down="green",  # 下跌K线的颜色
            edge="black",  # 蜡烛图箱体的颜色
            volume="blue",  # 成交量柱子的颜色
            wick="black"  # 蜡烛图影线的颜色
        )

        # 调用make_mpf_style函数，自定义图表样式
        # 函数返回一个字典，查看字典包含的数据，按照需求和规范调整参数
        # The Images Below show 2000 rows of  data, first as type='candle' and then as type='line'.
        style = mpf.make_mpf_style(base_mpl_style="ggplot", marketcolors=mc)
        mpf.plot(
            data=draw_df,
            type="candle",
            title=index_name,
            # ylabel="price",
            style=style,
            volume=False,
            addplot=add_plot,
            savefig = save_path

        )

    @staticmethod
    def long_vis(index_df,index_name):
        '''
        输入1000个交易日左右的数据
        输出open构成的折线 + 笔（拐点）
        '''

        ### K线、分型、笔的可视化
        draw_df = index_df[['DATETIME', 'open', 'high', 'low', 'close', 'parting', 'pen_point']].copy()

        ## 生成part和pen的标注点
        def part_pen_up_func(parting, open):
            if parting == 1:
                return open + 0
            else:
                return np.nan

        def part_pen_down_func(parting, open):
            if parting == -1:
                return open - 0
            else:
                return np.nan


        # draw_part为分型part的标记高度，part_pen为笔pen的标记高度。
        draw_df['draw_part_up'] = draw_df.apply(lambda row: part_pen_up_func(row['parting'], row['open']), axis=1)
        draw_df['draw_part_down'] = draw_df.apply(lambda row: part_pen_down_func(row['parting'], row['open']), axis=1)
        draw_df['draw_pen_up'] = draw_df.apply(lambda row: part_pen_up_func(row['pen_point'], row['open']), axis=1)
        draw_df['draw_pen_down'] = draw_df.apply(lambda row: part_pen_down_func(row['pen_point'], row['open']), axis=1)



        ## 用原始高开低收数据生成k线
        draw_df['DATETIME'] = pd.to_datetime(draw_df['DATETIME'], format='%Y-%m-%d')


        plt.plot(draw_df['DATETIME'] ,draw_df.open,color = 'k',alpha = 0.7)
        plt.scatter(draw_df['DATETIME'] ,draw_df.draw_pen_up,marker='^',color = 'r',label = 'Downward inflection point')
        plt.scatter(draw_df['DATETIME'] ,draw_df.draw_pen_down,marker='^',color = 'g',label = 'Upward inflection point')
        plt.xticks(rotation=30)
        plt.ylabel('open')
        plt.title(index_name)
        plt.legend()
        save_path = './pic/long_vis_'+ index_name + '.jpg'
        # plt.savefig(save_path)

        plt.show()

    @staticmethod
    def true_pre_plot(draw_df,title_name = 'True_VS_Pre'):
        '''
        在open线上标记真实和预测拐点。
        :param series:
        :return:
        '''
        draw_df = draw_df.reset_index().copy()

        ## 生成part和pen的标注点
        def part_pen_up_func(parting, open):
            if parting == 1:
                return open + 0
            else:
                return np.nan

        def part_pen_down_func(parting, open):
            if parting == -1:
                return open - 0
            else:
                return np.nan

        # draw_part为分型part的标记高度，part_pen为笔pen的标记高度。
        draw_df['draw_pre_up'] = draw_df.apply(lambda row: part_pen_up_func(row['signal'], row['open']), axis=1)
        draw_df['draw_pre_down'] = draw_df.apply(lambda row: part_pen_down_func(row['signal'], row['open']), axis=1)
        draw_df['draw_true_up'] = draw_df.apply(lambda row: part_pen_up_func(row['flag'], row['open']), axis=1)
        draw_df['draw_true_down'] = draw_df.apply(lambda row: part_pen_down_func(row['flag'], row['open']), axis=1)

        ## 用原始高开低收数据生成k线
        draw_df['DATETIME'] = pd.to_datetime(draw_df['DATETIME'], format='%Y-%m-%d')

        plt.figure(figsize=(15, 8));
        plt.plot(draw_df['DATETIME'], draw_df.open, color='k', alpha=0.5)
        plt.scatter(draw_df['DATETIME'], draw_df.draw_pre_up, marker='x', color='k',
                    label='Pre Downward inflection')
        plt.scatter(draw_df['DATETIME'], draw_df.draw_pre_down, marker='x', color='b',
                    label='Pre Upward inflection')
        plt.scatter(draw_df['DATETIME'], draw_df.draw_true_up, marker='^', color='r',
                    label='True Downward inflection')
        plt.scatter(draw_df['DATETIME'], draw_df.draw_true_down, marker='^', color='g',
                    label='True Upward inflection')
        plt.xticks(rotation=30)
        plt.ylabel('open')
        plt.title(title_name)
        plt.legend()
        save_path = './pic/'+ title_name + '_'+date.today().strftime('%Y%m%d')+ '.jpg'
        plt.savefig(save_path)
        plt.show()
        print('plot success')

    @staticmethod
    def draw_from_dict(dicdata, RANGE, heng=0):
        # dicdata：字典的数据。
        # RANGE：截取显示的字典的长度。
        # heng=0，代表条状图的柱子是竖直向上的。heng=1，代表柱子是横向的。考虑到文字是从左到右的，让柱子横向排列更容易观察坐标轴。
        by_value = sorted(dicdata.items(), key=lambda item: item[1], reverse = True)
        x = []
        y = []
        for d in by_value:
            x.append(d[0])
            y.append(d[1])
        plt.title('Feature Importance')
        if heng == 0:
            plt.bar(x[0:RANGE], y[0:RANGE])
            plt.show()
            return
        elif heng == 1:
            plt.barh(x[0:RANGE], y[0:RANGE])
            plt.show()
            return
        else:
            return "heng的值仅为0或1！"