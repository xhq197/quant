'''
#-*- coding: utf-8 -*-
@Author  : xiehuiqin
@Time    : 2022/2/9 17:08
@Function: 单模型和复合机器学习预测结果
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PROCESS import Processing
from DATA import handleData
import datetime
import xgboost as xgb
from xgboost import plot_importance
from sklearn.metrics import roc_auc_score
from sklearn.metrics import confusion_matrix,recall_score,roc_auc_score,precision_score
from VIS import ReversePointVis
from TRADE import run_trade
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn import svm

class multiModels:

    @staticmethod
    def XGB_train_func(params,validation_train_f,validation_train_l,validation_test_f,validation_test_l ):
        xgb_train = xgb.DMatrix(validation_train_f, label=validation_train_l)
        xgb_test = xgb.DMatrix(validation_test_f, label=validation_test_l)
        watchlist = [(xgb_train, 'train'), (xgb_test, 'val')]
        module = xgb.train(params, xgb_train, num_boost_round=200, evals=watchlist)
        result = module.predict(xgb_test)
        features = module.get_fscore()
        # features = list(dict(sorted(features.items(), key=lambda d: d[1])).keys())  #[-5:]
        # features.reverse()
        # print(features)
        # plot_importance(module)
        # plt.show()
        plt.figure(figsize=(15,15))
        features_ratio = {k: v / total for total in (sum(features.values()),) for k, v in features.items()}
        ReversePointVis.draw_from_dict(features_ratio,20,1)
        print("auc:{0:.2%} ".format(roc_auc_score(validation_test_l.values, result)))
        return result,features

    @staticmethod
    def judge(test_l,pre,model_name = 'model'):
        '''
        输入两个series或np.array
        '''
        # test_l = test_l[-828:]
        # pre = pre[-828:]
        print('#### ' + model_name + ' ####')
        print('TN|FP')
        print('FN|TP')
        print(confusion_matrix(test_l,pre ))
        TN, FP, FN, TP = confusion_matrix(test_l,pre ).ravel()

        precision = TP / (TP+FP)  # 查准率
        recall = TP / (TP+FN)  # 查全率
        accuracy = (TP+TN)/(TP+FP+TN+FN)
        print('precision:{0:.2%}, recall:{1:.2%}, accuracy:{2:.2%}'.format(precision,recall,accuracy))
        print('#### judge end ####')

    @staticmethod
    def get_split_xy(way_num):
        '''
        :param way_num:
        :return:
        '''

        ## 读入数据 1 V 0
        raw_std_index = Processing.get_std_index()
        std_index = handleData.change_flag(raw_std_index, way_num)
        train_x, train_y, validation_test_f, validation_test_l = Processing.data_split(std_index)
        smote_train_x_out, smote_train_y_out = Processing.up_sampling(train_x, train_y)
        return smote_train_x_out,smote_train_y_out,validation_test_f,validation_test_l

    @staticmethod
    def get_res_df(best_test_pre,validation_test_l):
        '''
        :param best_test_pre:
        :return: 包含open、flag原始标签、target正负一同步的标签、pre预测的标签的df
        '''
        # 1 V 0
        raw_data = pd.read_csv('./data/sz50_flag.csv', index_col=0)
        raw_data.DATETIME = pd.to_datetime(raw_data.DATETIME)
        raw_data.set_index('DATETIME', inplace=True)
        raw_data.flag = raw_data.flag.fillna(0)
        test_l_pre = validation_test_l.copy()
        test_l_pre['pre'] = best_test_pre

        vic_data = raw_data.iloc[:, [0, -1]].merge(test_l_pre, left_index=True, right_index=True, how='left')
        vic_data = vic_data[vic_data.index >= '2016-12-07']

        # flag + shift(-1)还原
        vic_data.flag = vic_data.flag.shift(1)
        vic_data.target = vic_data.target.shift(1)
        vic_data.pre = vic_data.pre.shift(1)
        return vic_data

    @staticmethod
    def run_XGB(way_num :int):
        '''
        :param index: 含有flag和feature的df
        :return:
        '''
        # XGB params
        params1 = {
            'booster': 'gbtree',
            'objective': 'binary:logistic',
            'gamma': 0.1,  # 用于控制是否后剪枝的参数,越大越保守，一般0.1、0.2这样子。
            'max_depth': 3,  # 构建树的深度，越大越容易过拟合
            'lambda': 4,  # 控制模型复杂度的权重值的L2正则化项参数，参数越大，模型越不容易过拟合。
            'alpha': 3,  # 权重的L1正则化项。
            'subsample': 0.5,  # 随机采样训练样本
            'colsample_bytree': 0.8,  # 生成树时进行的列采样
            'min_child_weight': 10,
            'silent': 0,  # 设置成1则没有运行信息输出，最好是设置为0.
            'eta': 0.03,  # 如同学习率
            'eval_metric': 'auc'

        }
        smote_train_x_out, smote_train_y_out, validation_test_f, validation_test_l = multiModels.get_split_xy(way_num)
        XGB_test_prob1,XGB_imp_f1  = multiModels.XGB_train_func(params1, smote_train_x_out, smote_train_y_out, validation_test_f,\
                                                  validation_test_l)
        best_test_pre = np.where(XGB_test_prob1 >= 0.6, 1, 0)
        multiModels.judge(validation_test_l, best_test_pre,'XGB')
        resDf = multiModels.get_res_df(best_test_pre,validation_test_l)
        return resDf

    @staticmethod
    def get_trade_single(vic_data_1,vic_data_m1):
        vic_data_m1['pre'] = -vic_data_m1['pre']
        trade_signal = pd.merge(vic_data_1[['open','flag','pre']],vic_data_m1['pre'],left_index = True,right_index = True,how = 'left')
        trade_signal['signal'] = trade_signal['pre_x'] + trade_signal['pre_y']
        return trade_signal

    @staticmethod
    def LR_train_func(train_feature, train_label, test_feature, test_label):
        print('开始训练logisticRegression模型:')
        LR_module = LogisticRegression(penalty='l2', solver='sag', max_iter=500, \
                                       random_state=42, n_jobs=4)  # class_weight={0:0.924,1:0.076}
        # module = lgb.LGBMClassifier(
        #     num_leaves=64,  # num_leaves = 2^max_depth * 0.6 #
        #     max_depth=6,
        #     n_estimators=80,
        #     learning_rate=0.1
        # )
        '''训练集'''
        LR_module.fit(train_feature, train_label)
        train_accurcy = LR_module.score(train_feature, train_label) * 100
        test_accurcy = LR_module.score(test_feature, test_label) * 100
        test_predict = LR_module.predict_proba(test_feature)
        print("训练集正确率为%.2s%%" % train_accurcy)
        print("测试集正确率为%.2s%%" % test_accurcy)
        return test_predict[:, 1]

    @staticmethod
    def run_LR(way_num):
        smote_train_x_out, smote_train_y_out, validation_test_f, validation_test_l = multiModels.get_split_xy(way_num)
        LR_test_prob = multiModels.LR_train_func(smote_train_x_out, smote_train_y_out, validation_test_f,
                                                 validation_test_l)
        best_test_pre = np.where(LR_test_prob >= 0.6, 1, 0)
        multiModels.judge(validation_test_l, best_test_pre,'LR')
        resDf = multiModels.get_res_df(best_test_pre,validation_test_l)
        return resDf

    @staticmethod
    def run_RF(way_num):
        smote_train_x_out, smote_train_y_out, validation_test_f, validation_test_l = multiModels.get_split_xy(way_num)
        RF_module1 = RandomForestClassifier(n_estimators=20, max_depth=13, min_samples_split=80,
                                            min_samples_leaf=20, max_features=7, oob_score=True, random_state=10)
        RF_module1.fit(smote_train_x_out, smote_train_y_out.values.ravel())
        RF_module1.oob_score_
        RF_test_prob1 = RF_module1.predict_proba(validation_test_f)[:, 1]

        best_test_pre = np.where(RF_test_prob1 >= 0.6, 1, 0)
        multiModels.judge(validation_test_l, best_test_pre,'RF')
        resDf = multiModels.get_res_df(best_test_pre,validation_test_l)
        return resDf

    @staticmethod
    def run_SVM(way_num):

        smote_train_x_out, smote_train_y_out, validation_test_f, validation_test_l = multiModels.get_split_xy(way_num)
        # 选 linear
        print('#### kernel = linear ####')
        clf_rbf = svm.SVC(kernel='rbf', probability=True)
        clf_rbf.fit(smote_train_x_out, smote_train_y_out.values.ravel())
        best_test_pre = clf_rbf.predict(validation_test_f)  # 模型对测试集的预测结果
        print('*** pre ***')
        multiModels.judge(validation_test_l, best_test_pre)
        resDf = multiModels.get_res_df(best_test_pre,validation_test_l)
        return resDf




if __name__ == '__main__':
    # XGB
    # vic_data_1 = multiModels.run_XGB(1)
    # vic_data_m1 = multiModels.run_XGB(2)
    # trade_signal = multiModels.get_trade_single(vic_data_1,vic_data_m1)
    # run_trade.myTradeMain(trade_signal,3)

    #LR
    # vic_data_1 = multiModels.run_LR(1)
    # vic_data_m1 = multiModels.run_LR(2)
    # trade_signal = multiModels.get_trade_single(vic_data_1,vic_data_m1)
    # run_trade.myTradeMain(trade_signal,3)

    #RF
    # vic_data_1 = multiModels.run_RF(1)
    # vic_data_m1 = multiModels.run_RF(2)
    # trade_signal = multiModels.get_trade_single(vic_data_1,vic_data_m1)
    # run_trade.myTradeMain(trade_signal,3)

    #SVM
    # vic_data_1 = multiModels.run_SVM(1)
    # vic_data_m1 = multiModels.run_SVM(2)
    # trade_signal = multiModels.get_trade_single(vic_data_1,vic_data_m1)
    # # trade_signal = trade_signal.loc[trade_signal.index >= '2018-08-20']
    # run_trade.myTradeMain(trade_signal,3)

    # #模型合并
    # # XGB + SVM
    # vic_data_1_XGB = multiModels.run_XGB(1)
    # vic_data_m1_XGB = multiModels.run_XGB(2)
    #
    # vic_data_1_SVM = multiModels.run_SVM(1)
    # vic_data_m1_SVM = multiModels.run_SVM(2)
    #
    # vic_data_1 = vic_data_1_XGB.copy()
    # vic_data_m1 = vic_data_m1_XGB.copy()
    # print('##### XGB + SVM >= 1 #####')
    # vic_data_1.pre = np.where(vic_data_1_XGB.pre + vic_data_1_SVM.pre >= 1,1,0)
    # vic_data_m1.pre = np.where(vic_data_m1_XGB.pre + vic_data_m1_SVM.pre >= 1, 1, 0)
    # trade_signal = multiModels.get_trade_single(vic_data_1,vic_data_m1)
    # run_trade.myTradeMain(trade_signal,3)
    #
    #
    # print('##### XGB + SVM >= 2 #####')
    # vic_data_1.pre = np.where(vic_data_1_XGB.pre + vic_data_1_SVM.pre >= 2,1,0)
    # vic_data_m1.pre = np.where(vic_data_m1_XGB.pre + vic_data_m1_SVM.pre >= 2, 1, 0)
    # trade_signal = multiModels.get_trade_single(vic_data_1,vic_data_m1)
    # run_trade.myTradeMain(trade_signal,3)
    #
    # # 四个模型
    #
    # ## 模型一：加权复合模型
    print('##### 4 models #####')
    vic_data_1 = pd.read_csv('./res/20220126_1.csv',index_col = 0)
    vic_data_m1 = pd.read_csv('./res/20220126_-1.csv',index_col = 0)
    vic_data_m1['pre'] = -vic_data_m1['pre']
    trade_signal = pd.merge(vic_data_1[['open','flag','pre']],vic_data_m1['pre'],left_index = True,right_index = True,how = 'left')
    trade_signal['signal'] = trade_signal['pre_x'] + trade_signal['pre_y']
    run_trade.myTradeMain(trade_signal, 1)






















