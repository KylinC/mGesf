import datetime

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
import numpy as np

from Learn.data_in import resolve_points_per_sample
from utils.data_utils import load_idp
from utils.learn_utils import make_model, make_model_simple
from tensorflow.python.keras.callbacks import EarlyStopping, ModelCheckpoint

import matplotlib.pyplot as plt

# idp_complete_classes = ['A', 'B', 'C', 'D', 'E',
#                         'F', 'G', 'H', 'I', 'J',
#                         'K', 'L', 'M', 'N', 'O',
#                         'P', 'Q', 'R', 'S', 'T',
#                         'U', 'V', 'W', 'X', 'Y',
#                         'Z', 'Spc', 'Bspc', 'Ent', 'Act']

idp_complete_classes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

sensor_feature_dict = {'mmw': ('range_doppler', 'range_azi')}
sensor_period_dict = {'mmw': 33.45}
input_interval = 4.0
sensor_sample_points_dict = dict([(key, (resolve_points_per_sample(value, input_interval))) for key, value in sensor_period_dict.items()])

encoder = OneHotEncoder(categories='auto')
encoder.fit(np.reshape(idp_complete_classes, (-1, 1)))
X_dict, Y = load_idp('D:\PcProjects\mGesf\data\data_ev1\hw_cr_ABCDEFGHIJ',
                     sensor_feature_dict=sensor_feature_dict,
                     complete_class=idp_complete_classes, encoder=encoder, sensor_sample_points_dict=sensor_sample_points_dict)

#####################################################################################
X_mmw_rD = X_dict['range_doppler']
X_mmw_rA = X_dict['range_azi']

# min-max normalize
X_mmw_rD = (X_mmw_rD - np.min(X_mmw_rD)) / (np.max(X_mmw_rD) - np.min(X_mmw_rD))
X_mmw_rA = (X_mmw_rA - np.min(X_mmw_rA)) / (np.max(X_mmw_rA) - np.min(X_mmw_rA))

# z normalize
# X_mmw_rD_zScore = (X_mmw_rD - np.mean(X_mmw_rD))/np.std(X_mmw_rD)
# X_mmw_rA_zScore = (X_mmw_rA - np.mean(X_mmw_rA))/np.std(X_mmw_rA)

X_mmw_rD_train, X_mmw_rD_test, Y_train, Y_test = train_test_split(X_mmw_rD, Y, test_size=0.20, random_state=3,
                                                                  shuffle=True)
X_mmw_rA_train, X_mmw_rA_test, Y_train, Y_test = train_test_split(X_mmw_rA, Y, test_size=0.20, random_state=3,
                                                                  shuffle=True)

#####################################################################################
model = make_model_simple(classes=idp_complete_classes, points_per_sample=sensor_sample_points_dict['mmw'])

es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=200)
mc = ModelCheckpoint(
    '../models/' + str(datetime.datetime.now()).replace(':', '-').replace(' ',
                                                                          '_') + '.h5',
    monitor='val_acc', mode='max', verbose=1, save_best_only=True)

history = model.fit(([X_mmw_rD_train, X_mmw_rA_train]), Y_train,
                    validation_data=([X_mmw_rD_test, X_mmw_rA_test], Y_test),
                    epochs=50000,
                    batch_size=32, callbacks=[es, mc], verbose=1, )

'''

'''
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

# summarize history for loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
