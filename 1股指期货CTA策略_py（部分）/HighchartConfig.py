# -*- coding: utf-8 -*-
# @Time     : 2020/08/06
# @Author   ：Li Wenting
# @File     : HighchartConfig.py
# @Software : PyCharm

'''配置highchart'''

from highcharts import Highstock


def add_offline_mode(H):
    highstock_css = ["http://orientlab.orientsec.com.cn:30080/static/highcharts/highslide.css"]
    highstock_js = ["http://orientlab.orientsec.com.cn:30080/static/highcharts/jquery.min.js",
                    "http://orientlab.orientsec.com.cn:30080/static/highcharts/highstock.js",
                    "http://orientlab.orientsec.com.cn:30080/static/highcharts/exporting.js",
                    "http://orientlab.orientsec.com.cn:30080/static/highcharts/highcharts-more.js",
                   ]
    H.JSsource.clear()
    H.CSSsource.clear()
    H.add_CSSsource(highstock_css)
    H.add_JSsource(highstock_js)
    return H

def options_for_candlestick(title = 'IC.CFE',y_title = 'OHLC'):
#     title = 'IC.CFE'
    width = '200px'
    valueDecimals = 4
    options = {
                'rangeSelector': {
                    'selected': 0
                },

                'title': {
                    'text': title
                },
                'tooltip': {
                    'style': {
                        'width': width
                    },
                    'valueDecimals': valueDecimals,
                    'shared': True
                },
                'yAxis': {
                    'title': {
                        'text': y_title
                    }
                },
                 'legend':{
                        'enabled':True,
                        'align':'center',
                    },
                'plotOptions': {
                    'candlestick': {
                        'color': 'green',
                        'upColor': 'red',
                    }
                },
            }
    return options

def options_for_line(title,y_title):
    # title = 'IC.CFE'
    width = '200px'
    valueDecimals = 4
    options = {
                'rangeSelector': {
                'selected': 0
                },
                'title': {
                    'text': title
                },
                'legend':{
                        'enabled':True,
                        'align':'center',
                    },
                'tooltip': {
                        'style': {
                        'width': width
                    },
                'valueDecimals': valueDecimals,
                'shared': True
                    },
                'yAxis': {
                    'title': {
                        'text': y_title
                        }
                    }
            }
    return options
def options_for_columns(title,y_title):
    options = {
                    'rangeSelector': {
                        'selected': 0
                    },
                    
                    'title': {
                        'text':title
                    },
                    'tooltip': {
                        'style': {
                            'width': '200px'
                        },
                        'valueDecimals':4,
                        'shared': True
                    },
                    'legend':{
                        'enabled':True,
                        'align':'center',
                    },
                    'yAxis': {
                        'title': {
                            'text': y_title
                        }
                    }
                }
    return options