import pandas as pd
import numpy as np
from keras.models import load_model
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


def predict(x_test,y_test,model,version_name):
    y_predict = model.predict_classes(x_test, verbose=1)
    label = [i[0] for i in y_test]

    # data = open("./DataSet/cnnmodel3.txt", 'w')
    # print('y_predict:\n',y_predict,'\n\n','validation_label:\n',label,file=data)
    # data.close()

    print('y_predict:\n',y_predict,'\n\n','validation_label:\n',label)

    pred = pd.Series(y_predict)
    label = pd.Series(label)
    res = pd.concat([label,pred],axis = 1)
    # loss, accuracy = model.evaluate(x_test, y_test)
    # print(loss, accuracy)
    # res.loc[0,'accuracy'] = accuracy
    # res.loc[0,'loss'] = loss
    #
    res.columns = ['true','pred']
    res.to_pickle(f'./result/test_res{version_name}.pkl')
    print('save done!')

if __name__ == '__main__':
    version_name = '6'
    x_test = np.load(f"./DataSet/x_test{version_name}.npy")
    y_test = np.load(f"./DataSet/y_test{version_name}.npy")
    model = load_model(f'./cnnmodel{version_name}.h5')
    predict(x_test, y_test, model,version_name)




#获取预测值，在notebook中计算评估指标

# def plot_confusion_matrix(confusion_mat):
#     plt.imshow(confusion_mat,interpolation='nearest',cmap=plt.cm.Paired)
#     plt.title('Confusion Matrix')
#     plt.colorbar()
#     tick_marks=np.arange(5)
#     plt.xticks(tick_marks,tick_marks)
#     plt.yticks(tick_marks,tick_marks)
#     plt.ylabel('True Label')
#     plt.xlabel('Predicted Label')
#     plt.show()
# confusion_matrix = tf.contrib.metrics.confusion_matrix(y_val,y_predict, num_classes=None, dtype=tf.int32, name=None, weights=None)
# sess = tf.Session()
# confusion_matrix = sess.run(confusion_matrix)
# plot_confusion_matrix(confusion_matrix)

#---------------------------

# #绘制ROC曲线
# -*- coding: utf-8 -*-
# import matplotlib.pyplot as plt
# from sklearn import svm
# from sklearn.metrics import roc_curve, auc  ###计算roc和auc
#
# train_x = [[0.], [1.], [1.], [0.], [1.]]
# train_y = [0., 1., 1., 0., 1.]
# test_x = [[1.], [1.], [0.], [1.], [0.]]
# test_y = [1., 1., 0., 1., 0.]
#
#
# # Learn to predict each class against the other
# svm = svm.SVC(kernel='linear', probability=True)
#
# ###通过decision_function()计算得到的y_score的值，用在roc_curve()函数中
# model = svm.fit(train_x, train_y)
# test_y_score = model.decision_function(test_x)
# prediction = model.predict(test_x)
# print(test_y_score)
# print(prediction)
# # Compute ROC curve and ROC area for each class
# fpr, tpr, threshold = roc_curve(test_y, test_y_score)  ###计算真正率和假正率
# roc_auc = auc(fpr, tpr)  ###计算auc的值
#
# lw = 2
# plt.figure(figsize=(8, 5))
# plt.plot(fpr, tpr, color='darkorange',
#          lw=lw, label='ROC curve (area = %0.2f)' % roc_auc)  ###假正率为横坐标，真正率为纵坐标做曲线
# plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
# plt.xlim([0.0, 1.0])
# plt.ylim([0.0, 1.05])
# plt.xlabel('False Positive Rate')
# plt.ylabel('True Positive Rate')
# plt.title('Receiver operating characteristic example')
# plt.legend(loc="lower right")
# plt.show()
