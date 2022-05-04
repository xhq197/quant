'''
#-*- coding: utf-8 -*-
@Author  : xiehuiqin
@Time    : 2022/1/28 2:34
@Function: 评估模型预测效果
'''
from sklearn import metrics
import pandas as pd

class judge_model:
    @staticmethod
    def evaluation(y_test, y_pre):
        '''
        多分类完整评估
        :param y_test: 实际测试集label,array(,n)，如array[1,0,1,0,-1]
        :param y_pre: 预测测试集label,array(,n)
        :return:
        '''
        print('########### model evaluation ##########')
        print(pd.crosstab(y_test, y_pre, rownames=['Actual'], colnames=['Predicted']))
        print(metrics.classification_report(y_test, y_pre))
        print("Accuracy: {:.2%}".format(metrics.accuracy_score(y_test, y_pre)))
        print("Cohen's Kappa: {:.2%}" .format(metrics.cohen_kappa_score(y_test, y_pre)))
        print('########### evaluation end ##########')

