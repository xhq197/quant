import keras
from keras.models import load_model
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D
import  numpy as np
import keras.backend.tensorflow_backend as KTF

import os
import tensorflow as tf
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'




#设定为自增长
config = tf.compat.v1.ConfigProto() #tf.ConfigProto()
config.gpu_options.allow_growth=True
session = tf.compat.v1.Session(config=config) #tf.Session(config=config)
# KTF.set_session(session)
# tf.compat.v1.keras.backend.set_session(session)
tf.compat.v1.keras.backend.set_session


####输入######
version_name = '6'
num_classes = 100
#15类分类
nppath = "./DataSet/"





# 加载数据
x_train = np.load(nppath + f"x_train{version_name}.npy")
x_test = np.load(nppath + f"x_test{version_name}.npy")
y_train = np.load(nppath + f"y_train{version_name}.npy")
y_test = np.load(nppath + f"y_test{version_name}.npy")

print(x_train.shape,y_train.shape,x_test.shape,y_test.shape)
#

x_train = x_train.astype('float64')/255
x_test = x_test.astype('float64')/255

# Convert class vectors to binary class matrices.
y_train = keras.utils.to_categorical(y_train, num_classes)
y_test = keras.utils.to_categorical(y_test, num_classes)



model = Sequential()

# model.add(Conv2D(32, (3, 3), padding='same', input_shape=x_train.shape[1:]))
# model.add(Activation('relu'))
#
# model.add(MaxPooling2D(pool_size=(2, 2)))
# model.add(Dropout(0.25))
#
# model.add(Conv2D(64, (3, 3), padding='same'))
# model.add(Activation('relu'))
#
# model.add(MaxPooling2D(pool_size=(2, 2)))
# model.add(Dropout(0.25))
#
# model.add(Flatten())
#
# model.add(Dense(512))
# model.add(Activation('relu'))
# model.add(Dropout(0.5))
#
# model.add(Dense(num_classes))
# model.add(Activation('relu'))
#
# model.summary()
#
#
# # train the model using RMSprop
# model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
#
# hist = model.fit(x_train, y_train, epochs=3, shuffle=True)

model.add(Conv2D(32, kernel_size=(1,1),input_shape=x_train.shape[1:], activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Conv2D(32, kernel_size=(5,5), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Flatten())

# beginning of fully connected neural network.
model.add(Dense(100, activation='relu'))
model.add(Dropout(0.5))
# Add fully connected layer with a softmax activation function
model.add(Dense(num_classes, activation='softmax'))

# Compile neural network
model.compile(loss='categorical_crossentropy', # Cross-entropy
                optimizer='rmsprop', # Root Mean Square Propagation
                metrics=['accuracy']) # Accuracy performance metric


# begin train the data
history = model.fit(x_train, # train data
            y_train, # label
            epochs=40, # Number of epochs
            verbose=2,
                batch_size=64)
model.save(f"./cnnmodel{version_name}.h5")

# evaluate
loss, accuracy = model.evaluate(x_test, y_test)

print(loss, accuracy)