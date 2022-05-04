#coding=utf-8


import pandas as pd

'''单变量特征选取'''
from sklearn.feature_selection import SelectKBest, chi2
'''去除方差小的特征'''
from sklearn.feature_selection import VarianceThreshold
'''循环特征选取'''
from sklearn.svm import SVC
from sklearn.feature_selection import RFE
'''RFE_CV'''
from sklearn.ensemble import ExtraTreesClassifier
from PROCESS import Processing


class FeatureSelection(object):
    def __init__(self, feature_num,is_score = False,precess_data_path = './data/CNN_std_index.csv'):
        self.precess_data_path = precess_data_path
        self.train_test, self.label =  self.read_data() # features #
        self.feature_name = list(self.train_test.columns)     # feature name #
        if not is_score:
            self.feature_num = feature_num
        else:
            self.feature_num = len(self.feature_name)


    def read_data(self):
        # train_test = pd.read_csv(self.precess_data_path, encoding='utf-8',index_col = 0)
        train_test = Processing.get_std_index()
        print('读取数据完毕。。。')
        label = train_test['target']
        train_test.drop('target',axis=1,inplace=True)
        return train_test, label

    def set_to_dict(self, set):
        lst = list(set)
        score_dict = {lst[i] : i +1 for i in range(len(lst))}
        return score_dict

    def add_dict(self,score_dict1,score_dict2):
        return {f:score_dict1[f] + score_dict2[f] for f in score_dict1}



    def variance_threshold(self):
        sel = VarianceThreshold()
        sel.fit_transform(self.train_test)
        feature_var = list(sel.variances_)    # feature variance #
        features = dict(zip(self.feature_name, feature_var))
        features = list(dict(sorted(features.items(), key=lambda d: d[1])).keys())[-self.feature_num:]
        print('VarianceThreshold:\n',features)   # 100 cols #
        return set(features)   # return set type #

    def select_k_best(self):
        ch2 = SelectKBest( k=self.feature_num) #默认f_classif，ch2：卡方检验，输入值必须为非负数和bool
        ch2.fit(self.train_test, self.label)
        feature_var = list(ch2.scores_)  # feature scores #
        features = dict(zip(self.feature_name, feature_var))
        features = list(dict(sorted(features.items(), key=lambda d: d[1])).keys())[-self.feature_num:]
        print('select_k_best:\n',features)     # 100 cols #
        return set(features)    # return set type #

    def svc_select(self):
        svc = SVC(kernel='rbf', C=1, random_state=2018)    # linear #
        rfe = RFE(estimator=svc, n_features_to_select=self.feature_num, step=1)
        rfe.fit(self.train_test, self.label.ravel())
        print('svc_select:\n',rfe.ranking_)
        return rfe.ranking_

    def tree_select(self):
        clf = ExtraTreesClassifier(n_estimators=300, max_depth=7, n_jobs=4)
        clf.fit(self.train_test, self.label)
        feature_var = list(clf.feature_importances_)  # feature scores #
        features = dict(zip(self.feature_name, feature_var))
        features = list(dict(sorted(features.items(), key=lambda d: d[1])).keys())[-self.feature_num:]
        print('tree_select:\n',features)     # 100 cols #
        return set(features)  # return set type #

    def return_feature_set(self, variance_threshold=False, select_k_best=False, svc_select=False, tree_select=False):
        names = set([])
        if variance_threshold is True:
            name_one = self.variance_threshold()
            names = names.union(name_one)
        if select_k_best is True:
            name_two = self.select_k_best()
            names = names.intersection(name_two)
        if svc_select is True:
            name_three = self.svc_select()
            names = names.intersection(name_three)
        if tree_select is True:
            name_four = self.tree_select()
            names = names.intersection(name_four)
        print('############## UNION RES ################')
        print(len(names))
        print('return_feature_set:\n',names)
        insert_idx = self.precess_data_path.rindex('.')
        save_path = self.precess_data_path[:insert_idx]
        save_path += '_selected_unoin.csv'
        self.train_test[list(names)].to_csv(save_path)
        print('*** 筛选后特征数据表（train_test）保存成功 ***')
        return list(names)

    def return_score_list(self, variance_threshold=False, select_k_best=False, svc_select=False, tree_select=False):
        names = {f:0 for f in self.train_test.columns}
        if variance_threshold is True:
            name_one = self.variance_threshold()
            names = self.add_dict(names, self.set_to_dict(name_one))
        if select_k_best is True:
            name_two = self.select_k_best()
            names = self.add_dict(names, self.set_to_dict(name_two))
        if svc_select is True:
            name_three = self.svc_select()
            names = self.add_dict(names, self.set_to_dict(name_three))
        if tree_select is True:
            name_four = self.tree_select()
            names = self.add_dict(names, self.set_to_dict(name_four))
        print('############## SCORE RES ################')
        print(len(names))
        sorted_names = sorted(names.items(),key = lambda x:x[1])
        sorted_names = [item[0] for item in sorted_names]
        print('return_sorted_names(重要程度依次递减):\n',sorted_names)
        return sorted_names


# # 筛选部分特征
# selection1 = FeatureSelection(60)
# selected_f = selection1.return_feature_set(variance_threshold=True, select_k_best=False, svc_select=False, tree_select=True)

# # 所有特征打分排序
# selection2 = FeatureSelection(103,True)
# f_score_sorted = selection2.return_score_list\
#     (variance_threshold=True, select_k_best=False, svc_select=False, tree_select=True)
