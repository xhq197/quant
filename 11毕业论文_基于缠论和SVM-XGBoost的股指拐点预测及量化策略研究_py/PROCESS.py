'''
#-*- coding: utf-8 -*-
@Author  : xiehuiqin
@Time    : 2022/1/27 19:51
@Function: 数据预处理
特征归一化，train标签1 -1 0
SMOTE让train平衡
'''
import pandas as pd
# 使用imlbearn库中上采样方法中的SMOTE接口
from imblearn.over_sampling import SMOTE  #, ADASYN


class Processing:
    @staticmethod
    def get_std_index():
        ## 读入数据
        index = pd.read_csv('./data/sz50_flag.csv',index_col = 0)
        index.DATETIME = pd.to_datetime(index.DATETIME)
        index.set_index('DATETIME',inplace = True)
        index.flag = index.flag.fillna(0)

        ## 处理空值

        '''处理前'''
        tmp_isnull = index.isnull().sum()
        # print(tmp_isnull[tmp_isnull > 0])
        index.div_compindex = index.div_compindex.fillna(0)
        tmp_isnull = index.isnull().sum()
        tmp_isnull = tmp_isnull[tmp_isnull > 0]
        for col in tmp_isnull.index:
            if col != 'flag':
                index.drop(col,axis = 1,inplace = True)
        '''处理后'''
        tmp_isnull = index.isnull().sum()
        # print(tmp_isnull[tmp_isnull > 0])

        ## 连续/离散变量分类
        '''离散变量'''
        unconti_col = []
        c = 0
        for i in range(len(index.columns[:-1])):
            if len(index.iloc[:,i].value_counts()) < 50:
                # print('离散特征：{0}'.format(index.columns[i]))
                unconti_col.append(index.columns[i])
                c = 1
        if c == 0:
            print('无离散特征')

        # print('总特征数：',len(index.columns) - 1)
        # print('离散特征数',len(unconti_col))

        '''连续变量'''
        conti_col = [col for col in index.columns[:-1] if col not in unconti_col]
        # print('连续特征数',len(conti_col))

        ## 均值填充
        for column in list(index.columns[index.isnull().sum() > 0]):
            mean_val = index[column].mean()
            index[column].fillna(mean_val, inplace=True)

        ## 归一化
        from sklearn.preprocessing import StandardScaler

        ## bool变量单独处理
        ss = StandardScaler()
        std_index = pd.DataFrame(ss.fit_transform(index[conti_col]),columns = list(conti_col),index = index.index)

        std_index = pd.DataFrame(std_index)
        std_index = std_index.merge(index[unconti_col],left_index = True,right_index = True,how = 'left')
        index.rename({'flag':'target'},axis = 1,inplace = True)
        std_index = std_index.merge(index['target'],left_index = True,right_index = True,how = 'left')
        # std_index.to_csv('./data/CNN_std_index.csv')
        # print('std_index of CNN have saved success!')
        return std_index

    @staticmethod
    def data_split(train_test_in):
        '''
        划分训练集和验证集
        :return:
        '''
        validation_train = train_test_in.iloc[:-int(len(train_test_in) * 0.3), :]
        validation_test = train_test_in.iloc[-int(len(train_test_in) * 0.3):, :]
        # validation_train = train_test_in[train_test_in.index < '2017-01-14']
        # validation_test = train_test_in[train_test_in.index >= '2017-01-14']

        '''validation_train'''
        validation_train_f = validation_train.drop(['target'], axis=1)
        validation_train_l = validation_train[['target']]
        print('train_x:', validation_train_f.shape)
        index = validation_train_f.copy()
        '''validation_test'''
        validation_test_f = validation_test.drop(['target'], axis=1)
        validation_test_l = validation_test[['target']]
        print('test_x:', validation_test_f.shape)

        index = validation_test_f.copy()
        return validation_train_f, validation_train_l, validation_test_f, validation_test_l

    @staticmethod
    def up_sampling(smote_train_x_in, smote_train_y_in):
        '''
        SMOTE上采样
        :param smote_train_x_in:
        :param smote_train_y_in:
        :return:
        '''
        # 定义SMOTE模型，random_state相当于随机数种子的作用
        smo = SMOTE(random_state=42)
        print('before SMOTE:\n',smote_train_y_in.target.value_counts())
        smote_train_x_out, smote_train_y_out = smo.fit_resample(smote_train_x_in, smote_train_y_in)
        print('SMOTE:\n', smote_train_y_out.target.value_counts())
        return smote_train_x_out, smote_train_y_out








