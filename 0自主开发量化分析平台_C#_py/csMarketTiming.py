import pandas as pd
import numpy as np

class MeanReversion:


    @staticmethod
    def contain_treat(prices, date_col='DATETIME', keep='last', col_move=None):

        prices_cp = prices.sort_values(by=[date_col])
        prices_cp.dropna(subset=['high', 'low'], inplace=True)
        prices_cp.reset_index(drop=True, inplace=True)
        prices_cp['k_num'] = prices_cp.index
        prices_cp['con_index'] = prices_cp.index  # con_index 为向上合并最高价出现位置，向下合并最低价出现位置
        prices_cp['con_sig'] = 1

        for i in range(1, len(prices_cp)):
            while True:
                high = prices_cp.loc[i, 'high']
                low = prices_cp.loc[i, 'low']
                sub = prices_cp.loc[0:i - 1]  # .where(prices_cp['con_sig'] == 1)
                sub = sub[sub['con_sig'] == 1]
                high_last = sub.iloc[- 1]['high']
                low_last = sub.iloc[- 1]['low']
                index_last = sub.index[- 1]
                con_index_last = sub.iloc[- 1]['con_index']

                if (high_last <= high and low_last >= low) or (high_last >= high and low_last <= low):
                    # treat the first two k line
                    if len(sub) == 1:  # TODO 2020/3/4 21:32 wgs:  how to adjust prices upward or downward
                        prices_cp.loc[i, 'high'] = max(high_last, high)
                        prices_cp.loc[i, 'low'] = min(low_last, low)
                        if high_last > high:
                            con_index = con_index_last
                        else:
                            con_index = i
                        prices_cp.loc[index_last, 'con_sig'] = 0
                        prices_cp.loc[i, 'con_index'] = con_index
                        break
                    else:
                        if high_last > sub.iloc[-2]['high']:  # 应该是具有非包含关系的K线，决定向上处理还是向下处理
                            prices_cp.loc[i, 'high'] = max(high_last, high)
                            prices_cp.loc[i, 'low'] = max(low_last, low)
                            if high_last > high:
                                con_index = con_index_last
                            else:
                                con_index = i

                        if high_last < sub.iloc[-2]['high']:
                            prices_cp.loc[i, 'high'] = min(high_last, high)
                            prices_cp.loc[i, 'low'] = min(low_last, low)
                            if low_last < low:
                                con_index = con_index_last
                            else:
                                con_index = i
                        prices_cp.loc[index_last, 'con_sig'] = 0
                        prices_cp.loc[i, 'con_index'] = con_index
                else:
                    break

        prices_cp_last = prices_cp[prices_cp['con_sig'] == 1]
        if keep == 'last':
            return prices_cp_last
        else:
            prices_cp_con = prices_cp_last.copy()
            prices_cp_con.index = prices_cp_con['con_index']
            prices_cp_con['DATETIME'] = prices_cp['DATETIME']  # 将时间定位在合并K线的高低点所在K线时间
            prices_cp_con['k_num'] = prices_cp['k_num']
            if 'open' in prices_cp.columns:
                prices_cp_con['open'] = prices_cp['open']
            if col_move:
                prices_cp_con[col_move] = prices_cp[col_move]
            return prices_cp_con

    @staticmethod
    def contain_treat_latest(prices_contained_last, prices_latest, date_col='DATETIME'):

        prices_latest_cp = prices_latest.copy()
        prices_latest_cp['k_num'] = prices_contained_last.iloc[- 1]['k_num'] + 1
        prices_latest_cp['con_sig'] = 1
        prices_cp = pd.concat([prices_contained_last, prices_latest_cp])
        prices_cp = prices_cp.sort_values(by=[date_col]).reset_index(drop=True)
        high = prices_latest_cp['high'].iloc[0]
        low = prices_latest_cp['low'].iloc[0]
        high_last = prices_contained_last.iloc[- 1]['high']
        low_last = prices_contained_last.iloc[- 1]['low']
        index_last = prices_cp.index[-2]
        index_latest = prices_cp.index[-1]

        if (high_last <= high and low_last >= low) or (high_last >= high and low_last <= low):
            # treat the first two k line
            if len(prices_contained_last) == 1:  # TODO 2020/3/4 21:32 wgs:  how to adjust prices upward or downward
                prices_cp.loc[index_latest, 'high'] = max(high_last, high)
                prices_cp.loc[index_latest, 'low'] = min(low_last, low)

            else:
                if high_last > prices_contained_last.iloc[-2]['high']:  # 应该是具有非包含关系的K线，决定向上处理还是向下处理
                    prices_cp.loc[index_latest, 'high'] = max(high_last, high)
                    prices_cp.loc[index_latest, 'low'] = max(low_last, low)

                if high_last < prices_contained_last.iloc[-2]['high']:
                    prices_cp.loc[index_latest, 'high'] = min(high_last, high)
                    prices_cp.loc[index_latest, 'low'] = min(low_last, low)
            prices_cp.loc[index_latest, 'open'] = prices_cp.loc[index_last, 'open']
            prices_cp.drop(index=index_last, inplace=True)
        prices_cp = prices_cp.reset_index(drop=True)
        return prices_cp

    @staticmethod
    def part(prices, date_col='DATETIME'):

        prices_cp = prices.sort_values(by=[date_col])
        prices_cp.reset_index(drop=True, inplace=True)
        prices_cp['parting'] = 0
        prices_cp['pen_point'] = 0
        prices_cp['parting_time'] = None
        last_parting = {'index': 0,
                        'k_num': prices_cp.loc[0, 'k_num'],
                        'parting': 0,
                        'price': None
                        }

        for i in range(2, len(prices_cp)):
            if prices_cp.loc[i - 1, 'high'] == max(prices_cp.loc[i - 2:i, 'high']):
                if prices_cp.loc[i, 'low'] < prices_cp.loc[i -2 , 'low'] and \
                        (prices_cp.loc[i, 'high'] < (prices_cp.loc[i - 2, 'high'] + prices_cp.loc[i - 2, 'low']) / 2):
                    prices_cp.loc[i - 1, 'parting'] = 2
                else:
                    prices_cp.loc[i - 1, 'parting'] = 1
                prices_cp.loc[i - 1, 'parting_time'] = prices_cp.loc[i, 'DATETIME']

                if (last_parting['parting'] < 0 and (prices_cp.loc[i - 1, 'k_num'] > last_parting['k_num'] + 3)) \
                        or last_parting['parting'] == 0:
                    prices_cp.loc[i - 1, 'pen_point'] = 1
                    prices_cp.loc[i - 1, 'pen_point_time'] = prices_cp.loc[i, 'DATETIME']
                    last_parting['index'], last_parting['k_num'], last_parting['parting'], last_parting['price'] = \
                        i - 1, prices_cp.loc[i - 1, 'k_num'], 1, prices_cp.loc[i - 1, 'high']
                if last_parting['parting'] > 0 and last_parting['price'] < prices_cp.loc[i - 1, 'high']:
                    prices_cp.loc[i - 1, 'pen_point'] = 1
                    prices_cp.loc[i - 1, 'pen_point_time'] = prices_cp.loc[i, 'DATETIME']
                    prices_cp.loc[last_parting['index'], 'pen_point'] = 10
                    last_parting['index'], last_parting['k_num'], last_parting['parting'], last_parting['price'] = \
                        i - 1, prices_cp.loc[i - 1, 'k_num'], 1, prices_cp.loc[i - 1, 'high']

            if prices_cp.loc[i - 1, 'low'] == min(prices_cp.loc[i - 2:i, 'low']):
                if prices_cp.loc[i, 'high'] > prices_cp.loc[i - 2, 'high'] and \
                        (prices_cp.loc[i, 'low'] > (prices_cp.loc[i - 2, 'high'] + prices_cp.loc[i - 2, 'low']) / 2):
                    prices_cp.loc[i - 1, 'parting'] = -2
                else:
                    prices_cp.loc[i - 1, 'parting'] = -1
                prices_cp.loc[i - 1, 'parting_time'] = prices_cp.loc[i, 'DATETIME']

                # judge the pen_point
                if (last_parting['parting'] > 0 and (prices_cp.loc[i - 1, 'k_num'] > last_parting['k_num'] + 3)) \
                        or last_parting['parting'] == 0:
                    prices_cp.loc[i - 1, 'pen_point'] = -1
                    prices_cp.loc[i - 1, 'pen_point_time'] = prices_cp.loc[i, 'DATETIME']
                    last_parting['index'], last_parting['k_num'], last_parting['parting'], last_parting['price'] = \
                        i - 1, prices_cp.loc[i - 1, 'k_num'], -1, prices_cp.loc[i - 1, 'low']
                if last_parting['parting'] < 0 and last_parting['price'] > prices_cp.loc[i - 1, 'low']:
                    prices_cp.loc[i - 1, 'pen_point'] = -1
                    prices_cp.loc[i - 1, 'pen_point_time'] = prices_cp.loc[i, 'DATETIME']
                    prices_cp.loc[last_parting['index'], 'pen_point'] = -10
                    last_parting['index'], last_parting['k_num'], last_parting['parting'], last_parting['price'] = \
                        i - 1, prices_cp.loc[i - 1, 'k_num'], -1, prices_cp.loc[i - 1, 'low']
        return prices_cp

    @staticmethod
    def part_old(prices, date_col='DATETIME'):

        prices_cp = prices.sort_values(by=[date_col])
        prices_cp.reset_index(drop=True, inplace=True)
        prices_cp['parting'] = 0
        prices_cp['pen_point'] = 0
        prices_cp['parting_time'] = None
        prices_cp['pen_point_time'] = None
        last_parting = {'index': 0,  # k线合并后的ID
                        'k_num': prices_cp.loc[0, 'k_num'],  # k 线的ID
                        'parting': 0,  # 分型类型
                        'price': None  # 前分型的最高价（顶分型）或最低价（底分型）
                        }

        for i in range(2, len(prices_cp)):
            # for i in range(2, 20):
            if prices_cp.loc[i - 1, 'high'] == max(prices_cp.loc[i - 2:i, 'high']):
                # and all(prices_cp.loc[i - 2:i - 1, 'parting'] == 0):
                if prices_cp.loc[i, 'low'] < prices_cp.loc[i - 2, 'low'] and \
                        (prices_cp.loc[i, 'high'] < (
                                prices_cp.loc[i - 2, 'high'] + prices_cp.loc[i - 2, 'low']) / 2):
                    prices_cp.loc[i - 1, 'parting'] = 2
                else:
                    prices_cp.loc[i - 1, 'parting'] = 1
                prices_cp.loc[i - 1, 'parting_time'] = prices_cp.loc[i, 'DATETIME']

                # judge the pen_point
                # date_i_1 = DateUtil.Timestamp_to_date(prices_cp.loc[i - 1, 'DATETIME'])
                if (last_parting['parting'] < 0 and (i - 1 > last_parting['index'] + 3)) \
                        or last_parting['parting'] == 0:
                    prices_cp.loc[i - 1, 'pen_point'] = 1
                    prices_cp.loc[i - 1, 'pen_point_time'] = prices_cp.loc[i, 'DATETIME']
                    last_parting['index'], last_parting['k_num'], last_parting['parting'], last_parting['price'] = \
                        i - 1, prices_cp.loc[i - 1, 'k_num'], 1, prices_cp.loc[i - 1, 'high']
                if last_parting['parting'] > 0 and last_parting['price'] < prices_cp.loc[i - 1, 'high']:
                    prices_cp.loc[i - 1, 'pen_point'] = 1
                    prices_cp.loc[i - 1, 'pen_point_time'] = prices_cp.loc[i, 'DATETIME']
                    prices_cp.loc[last_parting['index'], 'pen_point'] = 10
                    last_parting['index'], last_parting['k_num'], last_parting['parting'], last_parting['price'] = \
                        i-1, prices_cp.loc[i-1, 'k_num'], 1, prices_cp.loc[i-1, 'high']

            if prices_cp.loc[i - 1, 'low'] == min(prices_cp.loc[i - 2:i, 'low']):
                # and all(prices_cp.loc[i - 2:i - 1, 'parting'] == 0):
                if prices_cp.loc[i, 'high'] > prices_cp.loc[i - 2, 'high'] and \
                        (prices_cp.loc[i, 'low'] > (
                                prices_cp.loc[i - 2, 'high'] + prices_cp.loc[i - 2, 'low']) / 2):
                    prices_cp.loc[i - 1, 'parting'] = -2
                else:
                    prices_cp.loc[i - 1, 'parting'] = -1
                prices_cp.loc[i - 1, 'parting_time'] = prices_cp.loc[i, 'DATETIME']

                # judge the pen_point
                # date_i_1 = DateUtil.Timestamp_to_date(prices_cp.loc[i - 1, 'DATETIME'])
                if (last_parting['parting'] > 0 and (i - 1 > last_parting['index'] + 3)) \
                        or last_parting['parting'] == 0:
                    prices_cp.loc[i - 1, 'pen_point'] = -1
                    prices_cp.loc[i - 1, 'pen_point_time'] = prices_cp.loc[i, 'DATETIME']
                    last_parting['index'], last_parting['k_num'], last_parting['parting'], last_parting['price'] = \
                        i - 1, prices_cp.loc[i - 1, 'k_num'], -1, prices_cp.loc[i - 1, 'low']
                if last_parting['parting'] < 0 and last_parting['price'] > prices_cp.loc[i - 1, 'low']:
                    prices_cp.loc[i - 1, 'pen_point'] = -1
                    prices_cp.loc[i - 1, 'pen_point_time'] = prices_cp.loc[i, 'DATETIME']
                    prices_cp.loc[last_parting['index'], 'pen_point'] = -10
                    last_parting['index'], last_parting['k_num'], last_parting['parting'], last_parting['price'] = \
                        i - 1, prices_cp.loc[i - 1, 'k_num'], -1, prices_cp.loc[i - 1, 'low']
        return prices_cp

    @staticmethod
    def part_old_latest(part_last, prices_contained_latest, date_col='DATETIME'):

        part_last = part_last.sort_values(by=[date_col])
        part_last.reset_index(drop=True, inplace=True)
        prices_latest = prices_contained_latest.iloc[-1:, :].copy()
        part_last_datetime = part_last['DATETIME'].iloc[-1]

        if part_last_datetime >= prices_latest['DATETIME'].iloc[-1]:
            raise ValueError('Prices_contained_latest last DATETIME must greater than part_last DATETIME')
        if prices_latest.index[0] == part_last.index[-1]:
            if part_last['parting'].iloc[-1] != 0:
                part_last[['open', 'high', 'low', 'close']] = prices_latest[['open', 'high', 'low', 'close']]
                return part_last
            else:
                part_last.drop(index=part_last.index[-1], inplace=True)

        # else:
        prices_latest['parting'] = 0
        prices_latest['pen_point'] = 0
        prices_latest['parting_time'] = None
        prices_latest['pen_point_time'] = None
        part_last = pd.concat([part_last, prices_latest])
        part_last.reset_index(drop=True, inplace=True)
        part_last_index = part_last.index[-1]
        if len(part_last[part_last['pen_point'] != 0]):
            last_parting_info = part_last[part_last['pen_point'] != 0].iloc[-1]
            last_parting = {'index': last_parting_info.name,  # k线合并后的ID
                            'k_num': last_parting_info['k_num'],  # k 线的ID
                            'parting': last_parting_info['parting'],  # 分型类型
                            'price': last_parting_info['high' if last_parting_info['parting'] > 0 else 'low']
                            # 前分型的最高价（顶分型）或最低价（底分型）
                            }
        else:
            last_parting = {'index': 0,  # k线合并后的ID
                            'k_num': part_last.loc[0, 'k_num'],  # k 线的ID
                            'parting': 0,  # 分型类型
                            'price': None  # 前分型的最高价（顶分型）或最低价（底分型）
                            }

        if len(part_last) <= 2:
            part_last.reset_index(drop=True, inplace=True)
            return part_last

        if part_last.loc[part_last_index-1, 'high'] == max(
                part_last.loc[part_last_index - 2:part_last_index, 'high']):
            if part_last.loc[part_last_index, 'low'] < part_last.loc[part_last_index - 2, 'low'] and \
                    (part_last.loc[part_last_index, 'high'] < (part_last.loc[part_last_index - 2, 'high'] +
                                                                   part_last.loc[part_last_index - 2, 'low']) / 2):
                part_last.loc[part_last_index-1, 'parting'] = 2
            else:
                part_last.loc[part_last_index-1, 'parting'] = 1
            part_last.loc[part_last_index-1, 'parting_time'] = part_last.loc[part_last_index, 'DATETIME']

            if (last_parting['parting'] < 0 and (part_last_index-1 > last_parting['index'] + 3)) \
                    or last_parting['parting'] == 0:
                part_last.loc[part_last_index-1, 'pen_point'] = 1
                part_last.loc[part_last_index-1, 'pen_point_time'] = part_last.loc[part_last_index, 'DATETIME']
            if last_parting['parting'] > 0 and last_parting['price'] < part_last.loc[part_last_index-1, 'high']:
                part_last.loc[part_last_index-1, 'pen_point'] = 1
                part_last.loc[part_last_index-1, 'pen_point_time'] = part_last.loc[part_last_index, 'DATETIME']
                part_last.loc[last_parting['index'], 'pen_point'] = 10

        if part_last.loc[part_last_index-1, 'low'] == min(part_last.loc[part_last_index - 2:part_last_index + 2, 'low']):
            if part_last.loc[part_last_index, 'high'] > part_last.loc[part_last_index - 2, 'high'] and \
                    (part_last.loc[part_last_index, 'low'] > (part_last.loc[part_last_index - 2, 'high'] +
                                                                  part_last.loc[part_last_index - 2, 'low']) / 2):
                part_last.loc[part_last_index-1, 'parting'] = -2
            else:
                part_last.loc[part_last_index-1, 'parting'] = -1
            part_last.loc[part_last_index-1, 'parting_time'] = part_last.loc[part_last_index, 'DATETIME']

            # judge the pen_point
            if (last_parting['parting'] > 0 and (part_last_index-1 > last_parting['index'] + 3)) \
                    or last_parting['parting'] == 0:
                part_last.loc[part_last_index-1, 'pen_point'] = -1
                part_last.loc[part_last_index-1, 'pen_point_time'] = part_last.loc[part_last_index, 'DATETIME']
            if last_parting['parting'] < 0 and last_parting['price'] > part_last.loc[part_last_index-1, 'low']:
                part_last.loc[part_last_index-1, 'pen_point'] = -1
                part_last.loc[part_last_index-1, 'pen_point_time'] = part_last.loc[part_last_index, 'DATETIME']
                part_last.loc[last_parting['index'], 'pen_point'] = -10
        return part_last

    @staticmethod
    def pen_point_prices(prices_part, keep_updated_pen_point=False):

        parting_prices = prices_part[prices_part['pen_point'] != 0].copy()
        if not keep_updated_pen_point:
            parting_prices = parting_prices[parting_prices['pen_point'] != 10]
            parting_prices = parting_prices[parting_prices['pen_point'] != -10]
        parting_prices.reset_index(drop=True, inplace=True)
        parting_prices.loc[:, 'prices'] = [parting_prices.loc[i, 'high'] if parting_prices.loc[i, 'pen_point'] == 1 else
                                    parting_prices.loc[i, 'low'] for i in range(0, len(parting_prices))]
        return parting_prices

    @staticmethod
    def pivot_latest(pivot_last, trend_prices, trend_col='pen_point', accessible_time_col='pen_point_time'):

        pivot_last = pivot_last.copy()
        trend_prices = trend_prices[trend_prices[trend_col] != 10]
        trend_prices = trend_prices[trend_prices[trend_col] != -10]

        if not len(trend_prices):
            return pivot_last
        accessible_time = trend_prices[accessible_time_col].iloc[-1]
        # complete_time = trend_prices['DATETIME'].iloc[-1]
        pivot_last['DATETIME'] = trend_prices['DATETIME'].iloc[-1]
#         trend_prices = trend_prices.iloc[:-1, :]
        if pivot_last['pivot_start'] is None:
            if pivot_last['processed_time'] is not None:
                trend_prices = trend_prices[trend_prices['DATETIME'] >= pivot_last['processed_time']]
            if len(trend_prices) < 5:
                return pivot_last
            else:
                trend_prices = trend_prices[-5:]
                trend_prices.reset_index(drop=True, inplace=True)
                if trend_prices['prices'].iloc[0] > trend_prices['prices'].iloc[1]:
                    zd = max(trend_prices['prices'].iloc[1], trend_prices['prices'].iloc[3])
                    zg = min(trend_prices['prices'].iloc[2], trend_prices['prices'].iloc[4])
                    if zd >= zg:  # 判断是否存在三个同向K线的重合
                        return pivot_last
                    else:
                        pivot_last['pivot_time'] = accessible_time
                        pivot_last['pivot_start'] = trend_prices.loc[1, 'DATETIME']
                        # pivot_last['pivot_complete'] = complete_time
                        pivot_last['pivot_complete'] = trend_prices.loc[4,'DATETIME']
                        pivot_last['processed_time'] = trend_prices.loc[4, 'DATETIME']
                        pivot_last['last_pivot_end'] = None
                        pivot_last['zd'] = zd
                        pivot_last['zg'] = zg
                        pivot_last['dd'] = min(trend_prices.loc[range(1, 5, 2), 'prices'])
                        pivot_last['gg'] = max(trend_prices.loc[range(2, 5, 2), 'prices'])
                        # pivot_last['pivot_time'] = trend_prices.loc[4, accessible_time_col]
                        pivot_last['direction'] = 'rise_again'
                        return pivot_last
                else:
                    zg = min(trend_prices['prices'].iloc[1], trend_prices['prices'].iloc[3])
                    zd = max(trend_prices['prices'].iloc[2], trend_prices['prices'].iloc[4])
                    if zd >= zg:  # 判断是否存在三个同向K线的重合
                        return pivot_last
                    else:
                        pivot_last['pivot_time'] = accessible_time
                        pivot_last['pivot_start'] = trend_prices.loc[1, 'DATETIME']
                        # pivot_last['pivot_complete'] = complete_time
                        pivot_last['pivot_complete'] = trend_prices.loc[4, 'DATETIME']
                        pivot_last['processed_time'] = trend_prices.loc[4, 'DATETIME']
                        pivot_last['last_pivot_end'] = None
                        pivot_last['zd'] = zd
                        pivot_last['zg'] = zg
                        pivot_last['dd'] = min(trend_prices.loc[range(2, 5, 2), 'prices'])
                        pivot_last['gg'] = max(trend_prices.loc[range(1, 5, 2), 'prices'])
                        # pivot_last['pivot_time'] = trend_prices.loc[4, accessible_time_col]
                        pivot_last['direction'] = 'call_back'
                        return pivot_last
        else:
            trend_prices_latest = trend_prices[trend_prices['DATETIME'] >= pivot_last['processed_time']]
            if not len(trend_prices_latest):
                return pivot_last
            elif len(trend_prices_latest) == 1:
                if pivot_last['zd'] <= trend_prices_latest['prices'].iloc[0] <= pivot_last['zg']:
                    pivot_last['last_trend_date'] = trend_prices_latest['DATETIME'].iloc[0]
                    pivot_last['dd'] = min(pivot_last['dd'], trend_prices_latest['prices'].iloc[0])
                    pivot_last['gg'] = max(pivot_last['gg'], trend_prices_latest['prices'].iloc[0])
                    # pivot_last['last_pivot_end'] = None
                return pivot_last
            else:
                trend_prices_latest = trend_prices_latest[-2:]
                trend_prices_latest.reset_index(drop=True, inplace=True)
                if min(trend_prices_latest['prices']) > pivot_last['zg'] or max(trend_prices_latest['prices']) < \
                        pivot_last['zd']:
                    processed_time = pivot_last['processed_time']
                    pivot_last = {'DATETIME': None, 'pivot_time': None, 'pivot_start': None, 'pivot_complete': None,
                                  'last_pivot_end': trend_prices_latest['DATETIME'].iloc[0],
                                  'processed_time': processed_time,
                                  'zg': None, 'zd': None, 'gg': None, 'dd': None, 'direction': None}
                    # TODO 2020/7/31 15:16 wgs: 三买之后立刻回到中枢
                    # pivot_last['last_pivot_end'] = trend_prices_latest['DATETIME'].iloc[0]
                    # pivot_last['processed_time'] = None
                    return pivot_last
                    # return {'DATETIME': None,  'pivot_time': None, 'pivot_start': None,
                    #         'last_pivot_end': trend_prices_latest['DATETIME'].iloc[0],
                    #         'processed_time': None, 'zg': None, 'zd': None, 'gg': None, 'dd': None, 'direction': None}
                elif (pivot_last['zd'] <= trend_prices_latest['prices'].iloc[0] <= pivot_last['zg']) or \
                        (pivot_last['zd'] > trend_prices_latest['prices'].iloc[0] and
                         pivot_last['zg'] < trend_prices_latest['prices'].iloc[1]) or \
                        (pivot_last['zd'] > trend_prices_latest['prices'].iloc[1] and
                         pivot_last['zg'] < trend_prices_latest['prices'].iloc[0]):
                    pivot_last['processed_time'] = trend_prices_latest['DATETIME'].iloc[0]
                    pivot_last['dd'] = min(pivot_last['dd'], trend_prices_latest['prices'].iloc[0])
                    pivot_last['gg'] = max(pivot_last['gg'], trend_prices_latest['prices'].iloc[0])
                else:
                    pivot_last['processed_time'] = trend_prices_latest['DATETIME'].iloc[1]
                    pivot_last['dd'] = min(pivot_last['dd'], min(trend_prices_latest['prices']))
                    pivot_last['gg'] = max(pivot_last['gg'], max(trend_prices_latest['prices']))
                return pivot_last

    @staticmethod
    def pivot_all(trend_prices, trend_col='pen_point', accessible_time_col='pen_point_time'):

        pivot_latest = {'DATETIME': None, 'pivot_time': None, 'pivot_start': None, 'last_pivot_end': None,
                        'processed_time': None, 'zg': None, 'zd': None, 'gg': None, 'dd': None, 'direction': None}
        pivot_result = []
        for i in trend_prices['DATETIME'].to_list():
            trend_prices_sub = trend_prices.loc[trend_prices['DATETIME'] <= i, :]
            pivot_latest = MeanReversion.pivot_latest(pivot_latest, trend_prices_sub, trend_col, accessible_time_col)
            pivot_result.append(pd.DataFrame(pivot_latest, index=[i]))
            # pivot_result.append(pivot_latest)
        pivot = pd.concat(pivot_result)
        pivot_fill = pivot.fillna(method='backfill')
        # pivot_fill = pivot_fill.reindex(pivot[pivot['DATETIME'].notna()].index)
        # pivot_fill .drop(['last_trend_date', 'processed_time'], axis=1, inplace=True)
        # pivot_fill = pivot_fill[pivot_fill['DATETIME'] >= pivot_fill['pivot_start']]
        filter_index = [i for i in pivot_fill.index if (pivot_fill.loc[i, 'last_pivot_end'] is None or
                                                        pivot_fill.loc[i, 'DATETIME'] <= pivot_fill.loc[
                                                            i, 'last_pivot_end'])]
        pivot_fill = pivot_fill.reindex(filter_index)
        pivot_fill = pivot_fill.rename(columns={'last_pivot_end': 'pivot_end'})
        pivot_fill.reset_index(drop=True, inplace=True)
        return pivot_fill

    @staticmethod
    def pivot_prices_new(pivot_all, prices):

        pivot_prices_sigle = pivot_all[pivot_all['DATETIME'] == pivot_all['pivot_end']]
        pivot_prices = prices
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
        return pivot_prices

    @staticmethod
    def trading_point_level_3(pivot_latest, trend_low_level_latest, trend_low_level_last, trading_point_last,
                              accessible_time_col='pen_point_time'):
                              # accessible_time_col='DATETIME'):

        # TODO 2020/7/13 17:34 wgs: Availiable Ttime
        if not len(trend_low_level_last):
            return {}
        if len(trend_low_level_last) < 2 or pivot_latest['zg'] is None or not isinstance(pivot_latest['zg'], float):
            return {}
        # if trend_low_level_latest[accessible_time_col].iloc[0] < pivot_latest['pivot_time']:
        if trend_low_level_latest['DATETIME'].iloc[0] < pivot_latest['pivot_complete']:
            raise ValueError('Pivot in the future can not be used for cal trading point')

        trend_low_level = pd.concat([trend_low_level_last, trend_low_level_latest])
        # trend_low_level['trend_finished_time'] = trend_low_level[accessible_time_col].shift(-1)  # Finished trend
        trend_low_level['trend_finished_time'] = trend_low_level[accessible_time_col]  # Finished trend

        if np.prod(trend_low_level['pen_point'][-2:, ]) > 0:
            return trading_point_last
        else:
            if not len(trading_point_last) or trading_point_last['pivot_start'] != pivot_latest['pivot_start']:
                trading_point_last = {}
            # trend_later = trend_low_level[['DATETIME', 'prices', 'trend_finished_time', 'pen_point']].iloc[-3:-1]
            trend_later = trend_low_level[['DATETIME', 'prices', 'trend_finished_time', 'pen_point']].iloc[-2:]
            if trend_later['prices'].iloc[0] > pivot_latest['zg'] and \
                    trend_later['prices'].iloc[1] > pivot_latest['zg']:
                if (not len(trading_point_last) or trading_point_last['trading_point'] == 0) and \
                        trend_later['pen_point'].iloc[-1] < 0:
                    trading_point = {'DATETIME': trend_later['DATETIME'].iloc[1], 'trading_point': 3,
                                     'trading_point_time': max(trend_later['trend_finished_time'].iloc[1],
                                                               pivot_latest['pivot_time']),
                                     'pivot_start': pivot_latest['pivot_start']}
                else:
                    trading_point = trading_point_last
            elif trend_later['prices'].iloc[0] < pivot_latest['zd'] and \
                    trend_later['prices'].iloc[1] < pivot_latest['zd']:
                if (not len(trading_point_last) or trading_point_last['trading_point'] == 0) and \
                        trend_later['pen_point'].iloc[-1] > 0:
                    trading_point = {'DATETIME': trend_later['DATETIME'].iloc[1], 'trading_point': -3,
                                     'trading_point_time': max(trend_later['trend_finished_time'].iloc[1],
                                                               pivot_latest['pivot_time']),
                                     'pivot_start': pivot_latest['pivot_start']}
                else:
                    trading_point = trading_point_last
            elif trend_later['prices'].iloc[0] > pivot_latest['zg'] and trend_later['prices'].iloc[1] < pivot_latest['zg']:
                if not len(trading_point_last) or trading_point_last['trading_point'] == 3:
                    # 这里可以返回{}
                    trading_point = {'DATETIME': trend_later['DATETIME'].iloc[1], 'trading_point': 0,
                                     'trading_point_time': max(trend_later['trend_finished_time'].iloc[1],
                                                               pivot_latest['pivot_time']),
                                     'pivot_start': pivot_latest['pivot_start']}
                else:
                    trading_point = trading_point_last
            elif trend_later['prices'].iloc[0] < pivot_latest['zd'] and trend_later['prices'].iloc[1] > pivot_latest['zd']:
                if not len(trading_point_last) or trading_point_last['trading_point'] == -3:
                    trading_point = {'DATETIME': trend_later['DATETIME'].iloc[1], 'trading_point': 0,
                                     'trading_point_time': max(trend_later['trend_finished_time'].iloc[1],
                                                               pivot_latest['pivot_time']),
                                     'pivot_start': pivot_latest['pivot_start']}
                else:
                    trading_point = trading_point_last
            else:
                trading_point = trading_point_last
                # trading_point = {'DATETIME': trend_later['DATETIME'].iloc[1], 'trading_point': 0,
                #                  'trading_point_time': trend_later['trend_finished_time'].iloc[1]}

        return trading_point

    @staticmethod
    def trading_point_all_level_3(pivot_this_level_all, trend_low_level_all):

        pivot_this_level_all = pivot_this_level_all[pivot_this_level_all['zg'].notnull()]
        pivot_this_level_all.reset_index(drop=True, inplace=True)
        trading_point_list = []
        trading_point_last = {}
        trend_low_level_last = pd.DataFrame()
        for i in trend_low_level_all.index:
            # i = trend_low_level_all.index[0]
            trend_low_level_latest = trend_low_level_all.loc[i:i, :]
            # pivot_latest = pivot_this_level_all.loc[pivot_this_level_all['pivot_time'] <
            #                                         trend_low_level_latest['pen_point_time'].iloc[-1], :]
            pivot_latest = pivot_this_level_all.loc[pivot_this_level_all['pivot_complete'] <
                                                    trend_low_level_latest['DATETIME'].iloc[-1], :]
            if not len(pivot_latest):
                pivot_latest = pivot_latest.to_dict()
            else:
                pivot_latest = pivot_latest.iloc[-1].to_dict()
            trading_point_last = MeanReversion.trading_point_level_3(pivot_latest, trend_low_level_latest,
                                                                     trend_low_level_last, trading_point_last)
            trend_low_level_last = trend_low_level_all.loc[:i, :]
            # print('trading_point_last\n',trading_point_last)
            if trading_point_last != {}:
                trading_point_list.append(pd.DataFrame(trading_point_last, index=[i]))
                trading_point_all = pd.concat(trading_point_list)
            else:
                trading_point_all = pd.DataFrame()
        # print('333trading_point_all\n',trading_point_all,'\n',trading_point_all.columns)
        # trading_point_all = trading_point_all[trading_point_all['trading_point'] != 0].drop_duplicates()
        trading_point_all = trading_point_all.drop_duplicates()
        return trading_point_all
