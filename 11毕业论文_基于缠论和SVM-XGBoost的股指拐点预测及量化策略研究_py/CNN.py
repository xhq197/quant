'''
#-*- coding: utf-8 -*-
@Author  : xiehuiqin
@Time    : 2022/1/27 19:48
@Function: CNN + softmax 三分类
# Project Title: Stock Inflection Point Prediction Using CNN
'''
# ------------------------ Libaries used --------------------------------------
import tensorflow as tf
import pandas as pd
import os as os
import numpy as np
import time
from sklearn import metrics
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from PROCESS import Processing
import warnings
warnings.filterwarnings('ignore')
from JUDGE import judge_model
from DATA import handleData
from datetime import date
from VIS import ReversePointVis
from FEATURE import FeatureSelection

class runCNN:
    def __init__(self,n_feature,n_epochs):
        # 【注意】n_feature 需要是偶数
        self.n_feature = n_feature
        self.n_epochs = n_epochs

    def CNN_main(self):
        ## 读入数据
        raw_std_index = Processing.get_std_index()
        std_index = handleData.change_flag(raw_std_index, 3)
        train_x, train_y, test_x, test_y = Processing.data_split(std_index)
        train_x, train_y = Processing.up_sampling(train_x, train_y)
        raw_test_x = test_x.copy()  # 用于保存结果
        train_y = train_y.astype('int32')
        train_y.rename({'target': 'label'}, axis=1, inplace=True)
        test_y = test_y.astype('int32')
        test_y.rename({'target': 'label'}, axis=1, inplace=True)
        fs = FeatureSelection(103,True)
        selected_feature = fs.return_score_list(variance_threshold=True, select_k_best=False,\
                             svc_select=False, tree_select=True)[-self.n_feature:]
        train_x = train_x[selected_feature]
        test_x = test_x[selected_feature]

        # ----------------- read in data & make data grid_like ------------------------
        x_train = np.array(train_x)
        x_test = np.array(test_x)
        y_train_encoded = np.array(pd.get_dummies(train_y.label))
        y_test_encoded = np.array(pd.get_dummies(test_y.label))
        y_test = np.array(test_y)
        y_test = y_test.reshape(1, -1)[0]
        # print('######shape######')
        # print(x_train.shape)
        # print(x_test.shape)
        # print(y_train_encoded.shape)
        # print(y_test_encoded.shape)
        # print(y_test.shape)
        # print(y_test)

        # make training set grid_like
        cnn_input = []
        for i in range(x_train.shape[0] - 50):
            row = []
            for k in range(50):
                for t in range(self.n_feature):
                    row.append(x_train[i + k, :][t])
            cnn_input.append(row)
        x_train_grid = pd.DataFrame(cnn_input)  # df
        check = y_train_encoded[0:-50, :]

        # make test set grid_like
        cnn_input_test = []
        for i in range(x_test.shape[0] - 50):
            row = []
            for k in range(50):
                for t in range(self.n_feature):
                    row.append(x_test[i + k, :][t])
            cnn_input_test.append(row)
        x_test_grid = pd.DataFrame(cnn_input_test)
        y_test_grid = y_test[0:-50]
        y_test_grid_encoded = y_test_encoded[0:-50, :]

        # --------------------------- Build Computation Graph -------------------------
        # Step 1: Define parameters for the CNN
        # Input
        height = 50
        width = self.n_feature
        channels = 1
        n_inputs = 50 * self.n_feature  # 50*n_feature

        # Parameters for TWO convolutional layers:
        conv1_fmaps = 36  # 36 # 18
        conv1_ksize = 2
        conv1_stride = 1
        conv1_pad = 'SAME'

        conv2_fmaps = 72  # 72
        conv2_ksize = 2
        conv2_stride = 1
        conv2_pad = 'SAME'

        # Define a pooling layer
        pool3_dropout_rate = 0.25
        pool3_fmaps = conv2_fmaps

        # Define a fully connected layer
        n_fc1 = 128  # 144           # units for the first fully connected layer
        fc1_dropout_rate = 0.5  # 0.5

        # Output
        n_outputs = 3
        learning_rate = 0.001

        # batch size
        batch_size = 50

        tf.compat.v1.reset_default_graph()  # reset_default_graph() is deprecated

        # Step 2: Set up placeholders for input data
        with tf.name_scope("inputs"):
            X = tf.placeholder(tf.float32, shape=[None, n_inputs], name="X")
            X_reshaped = tf.reshape(X, shape=[-1, height, width, channels])
            y = tf.placeholder(tf.int32, shape=[None, n_outputs], name="y")
            training = tf.placeholder_with_default(False, shape=[], name='training')
            # placeholder for training, default value is False

        # Step 3: Set up the two convolutional layers using tf.layers.conv2d
        conv1 = tf.layers.conv2d(X_reshaped, filters=conv1_fmaps, kernel_size=conv1_ksize,
                                 strides=conv1_stride, padding=conv1_pad, activation=tf.nn.relu,
                                 name='conv1')
        conv2 = tf.layers.conv2d(conv1, filters=conv2_fmaps, kernel_size=conv2_ksize,
                                 strides=conv2_stride, padding=conv2_pad, activation=tf.nn.relu,
                                 name='conv2')

        # Step 4: Set up the pooling layer with dropout using tf.nn.max_pool
        with tf.name_scope("pool3"):
            pool3 = tf.nn.max_pool(conv2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding="VALID")  # 1, 2, 1, 1
            pool3_flat = tf.reshape(pool3, shape=[-1, int(
                pool3_fmaps * 25 * self.n_feature / 2)])  # will go to fully connected dense layers, so reshape to 1-d tensor
            pool3_flat_drop = tf.layers.dropout(pool3_flat, pool3_dropout_rate,
                                                training=training)  # training placeholder, False.

        # Step 5: Set up the fully connected layer using tf.layers.dense
        with tf.name_scope("fc1"):
            fc1 = tf.layers.dense(pool3_flat_drop, n_fc1, activation=tf.nn.relu, name="fc1")  # width of layer: n_fc1
            fc1_drop = tf.layers.dropout(fc1, fc1_dropout_rate, training=training)

        with tf.name_scope("output"):
            logits = tf.layers.dense(fc1_drop, n_outputs, name="output")
            Y_proba = tf.nn.softmax(logits, name="Y_proba")

        # Step 5: Define the optimizer; taking as input (learning_rate) and (loss)
        with tf.name_scope("loss"):
            xentropy = tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=y)
            loss = tf.reduce_mean(xentropy, name="loss")
            loss_summary = tf.summary.scalar('log_loss', loss)

        with tf.name_scope("train"):
            optimizer = tf.train.AdamOptimizer(
                learning_rate)  # GradientDescentOptimizer #MomentumOptimizer , momentum=0.9
            training_op = optimizer.minimize(loss)

        # Step 6: Define the evaluation metric
        with tf.name_scope("eval"):
            correctPrediction = tf.equal(tf.argmax(Y_proba, 1), tf.argmax(y, 1))
            accuracy = tf.reduce_mean(tf.cast(correctPrediction, tf.float32))
            accuracy_summary = tf.summary.scalar('accuracy', accuracy)
        #    correct = tf.nn.in_top_k(logits, y, 1)
        #    accuracy = tf.reduce_mean(tf.cast(correct, tf.float32))

        # Step 7: Initiate
        with tf.name_scope("init_and_save"):
            init = tf.global_variables_initializer()
            saver = tf.train.Saver()

        # Step 9: Define some necessary functions
        def get_model_params():
            gvars = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES)  # get all the variables in the computation graph
            return {gvar.op.name: value for gvar, value in zip(gvars, tf.get_default_session().run(gvars))}

        def restore_model_params(model_params):
            gvar_names = list(model_params.keys())
            assign_ops = {gvar_name: tf.get_default_graph().get_operation_by_name(gvar_name + "/Assign")
                          for gvar_name in gvar_names}
            init_values = {gvar_name: assign_op.inputs[1] for gvar_name, assign_op in assign_ops.items()}
            feed_dict = {init_values[gvar_name]: model_params[gvar_name] for gvar_name in gvar_names}
            tf.get_default_session().run(assign_ops, feed_dict=feed_dict)

        def batch_func(X, y, batch_size):
            batches = []
            for i in range(0, len(X), batch_size):
                X_batch = X[i: i + batch_size]
                y_batch = y[i: i + batch_size]
                mini_batch = (X_batch, y_batch)
                batches.append(mini_batch)
            return batches

        # ---------------------------- Training Model ---------------------------------
        # Step 10: Define training and evaluation parameters
        iteration = 0

        best_loss_val = np.infty
        check_interval = 10  # 500
        checks_since_last_progress = 0
        max_checks_without_progress = 10  # 20
        best_model_params = None

        merged = tf.summary.merge_all()

        # Step 11: Train and evaluate CNN with Early Stopping procedure defined at the very top
        start = time.time()
        with tf.Session() as sess:
            init.run()
            train_writer = tf.summary.FileWriter('./graphs/train',
                                                 tf.get_default_graph())  # train_dropout_0.2 #train_layer_2
            test_writer = tf.summary.FileWriter('./graphs/test',
                                                tf.get_default_graph())  # train_MomentumOptimizer_optimizer
            for epoch in range(self.n_epochs):
                for a_batch in batch_func(x_train_grid, check, batch_size):
                    (X_batch, y_batch) = a_batch
                    # print('y_batch:',y_batch.shape)
                    # print('X_batch',X_batch.shape)
                    sess.run(training_op, feed_dict={X: X_batch, y: y_batch, training: True})

                # print (X_batch.shape)
                # print (y_batch.shape)
                #            if iteration % check_interval == 0:
                #                loss_val = loss.eval(feed_dict={X: X_valid, y: y_valid})
                #                if loss_val < best_loss_val:
                #                    best_loss_val = loss_val
                #                    checks_since_last_progress = 0
                #                    best_model_params = get_model_params()
                #                else:
                #                    checks_since_last_progress += 1
                acc_batch = accuracy.eval(feed_dict={X: X_batch, y: y_batch})
                #        acc_val = accuracy.eval(feed_dict={X: X_valid, y: y_valid})
                #        print("Epoch {}, last batch accuracy: {:.4f}%, valid. accuracy: {:.4f}%, valid. best loss: {:.6f}".format(
                #                  epoch, acc_batch * 100, acc_val * 100, best_loss_val))
                print("Epoch {}, last batch accuracy: {:.4f}%".format(epoch, acc_batch * 100))
                #        if checks_since_last_progress > max_checks_without_progress:
                #            print("Early stopping!")
                #            break
                # measure validation accuracy, and write validate summaries to FileWriters
                test_summary, acc = sess.run([merged, accuracy], feed_dict={X: x_test_grid, y: y_test_grid_encoded})
                test_writer.add_summary(test_summary, epoch)
                print('Accuracy at step %s: %s' % (epoch, acc))

                # run training_op on training data, and add training summaries to FileWriters
                train_summary, _ = sess.run([merged, training_op], feed_dict={X: X_batch, y: y_batch})  # , training_op
                train_writer.add_summary(train_summary, epoch)

            train_writer.close()
            test_writer.close()

            save_path = saver.save(sess, "./CNN_stock_model.ckpt")

        # --------------------- Prediction and Calculation of Metrics -----------------
        with tf.Session() as sess:
            saver.restore(sess, "./CNN_stock_model.ckpt")  # load model parameters from disk
            Z = Y_proba.eval(feed_dict={X: x_test_grid})
            y_pred = np.argmax(Z, axis=1) - 1  # np.argmax return the index, e.g. 0, 1, 2 for -1, 0, 1, so subtract 1.

        # 保存预测结果
        # pre_res: open、flag、signal
        pre_res = pd.DataFrame(
            {'open': list(raw_test_x['open'])[-len(y_test_grid):], 'flag': y_test_grid, 'signal': y_pred}, \
            index=raw_test_x.index[-len(y_test_grid):])
        pre_res.to_csv('./res/CNN' + date.today().strftime('%Y%m%d') + '.csv')
        print('##### pre_res save success #####')
        ReversePointVis.true_pre_plot(pre_res)
        judge_model.evaluation(y_test_grid, y_pred)
        print('Took: %f seconds' % (time.time() - start))
        return  pre_res





