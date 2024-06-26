from keras.preprocessing.image import ImageDataGenerator
from tensorflow.python.keras import Model
from tensorflow.python.keras.applications import resnet as rn
from tensorflow.python.keras.layers import Dense, Input
from keras import backend as K
import tensorflow as tf
import keras
from keras.callbacks import ModelCheckpoint
from tensorflow.python.keras.applications.resnet import preprocess_input
import numpy as np


print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))
sess = tf.Session(config=tf.ConfigProto(log_device_placement=True))
config = tf.ConfigProto( device_count = {'GPU': 1, 'CPU': 128} )
sess = tf.Session(config=config)
keras.backend.set_session(sess)

"""Parameter"""
img_width, img_height = 112, 112
train_data_dir = '../Images/train'
validation_data_dir = '../Images/test'
epochs = 20
batch_size = 32
num_class = 10
accuracy_Values = np.asarray(np.zeros((epochs, 2)))

if K.image_data_format() == 'channels_first':
    input_shape = (3, img_width, img_height)
else:
    input_shape = (img_width, img_height, 3)
# Specify Model
new_input = Input(shape = (img_width, img_height, 3))
model = rn.ResNet50(include_top=False, pooling='avg', weights=None, input_tensor=new_input)
x = model.output
fc = Dense(num_class, activation='softmax', name='Output')(x)
new_model = Model(inputs=model.inputs, outputs = fc)
new_model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# this is the augmentation configuration we will use for training
train_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)

test_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)

train_generator = train_datagen.flow_from_directory(
    train_data_dir,
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode='categorical',
    color_mode='rgb',
    shuffle=True
)

validation_generator = test_datagen.flow_from_directory(
    validation_data_dir,
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode='categorical',
    color_mode='rgb',
    shuffle=True)

checkpoint = ModelCheckpoint("../Data/CIFAR_ResNet_Best.h5",
                             monitor='val_acc',
                             verbose = 1,
                             save_best_only = True,
                             mode='auto',
                             period = 1,
                             save_weights_only=False)
for iter in range(0,epochs):
    new_model.fit_generator(
        train_generator,
        epochs = 1,
        validation_data = validation_generator,
        verbose = 1,
        callbacks=[checkpoint]
    )
    new_model.save('../Data/CIFAR_ResNet_Iteration_' +str(iter)+ '.h5')