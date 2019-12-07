#!/usr/bin/env python
# coding: utf-8

#get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib.pyplot as plt
import numpy as np
from sklearn.feature_selection import VarianceThreshold
import pandas as pd
from keras.layers import Dense, Input
from keras.models import Model
import keras.backend as K
import os.path
import zipfile
import time

def readData(projectName, versionNum):
	dataPath = '../../WTP-data'
	projectDataPath = '%s/%s/%d' % (dataPath, projectName, versionNum)
	dataFileName='%s/Metrics.csv' % (projectDataPath)
	zipFileName='%s/Metrics.zip' % (projectDataPath)
	if (not os.path.isfile(dataFileName) and os.path.isfile(zipFileName)):
		print("Unzipping ",zipFileName)
		with zipfile.ZipFile(zipFileName, 'r') as zip_ref:
			zip_ref.extractall(projectDataPath)	
	# print('Reading data set '+dataFileName)
	return pd.read_csv(dataFileName) 

# def readData(projectName, versionNum):
# 	dataPath = '..\\..\\..\\WTP-data'
# 	dataFileName='%s/%s/%d/Features.csv' % (dataPath, projectName, versionNum)
# 	# print('Reading data set '+dataFileName)
# 	return pd.read_csv(dataFileName)

def kerasBugPrediction(projectName, versionNum, lastVersion):
	dataPath = '../../WTP-data'
	for prevVersionNum in range(versionNum+1, lastVersion+1):
		dfPrevVersion = readData(projectName, prevVersionNum)
		if prevVersionNum == versionNum+1:
			df0 = dfPrevVersion
		else:
			# print('Appending...')
			df0 = df0.append(dfPrevVersion,sort=False)

	# remove 2 first columns (class and package names) and last columns (buggy values)
	df = df0.iloc[:, 2:-3]

	# applying log transformation for large-value features
	criteria = df.max(axis=0)>100
	df[criteria.index[criteria]] = np.log(1+df[criteria.index[criteria]].values)
	#TODO: test wether concatinating log of these high value features to original and removing low variance ones has a better results

	# for column in df.columns:
	#	 df.hist(bins=30, column=column)

	pd.set_option('display.max_columns', 1000)
	# df.corrwith(df0.before_bugs).sort_values()

	from sklearn.preprocessing import StandardScaler

	print('Running transformation on data')
	transform = StandardScaler().fit(df.values)
	dt = transform.transform(df.values)
	labels = np.array(df0.before_bugs>0, dtype=np.float)

	# print(df.values.shape[1])
	# vt = VarianceThreshold(threshold=.3).fit(dt)
	# print(len(vt.get_support(indices=True)))
	# dt = dt[:, vt.get_support(indices=True)]

	#TODO: duplicate rows with before bugs value > 1
	#print(dt)
	print('is_buggy>0 count: ', np.count_nonzero(df0.is_buggy>0))
	print('before_bugs>0 count: ', np.count_nonzero(labels))


	threshold = 0.5
	beta=.3
	import keras
	from keras.layers import Dropout, BatchNormalization, ReLU
	from keras.optimizers import SGD, Adam

	import tensorflow as tf
	def f1_loss(y_true, y_pred):
		
		tp = K.sum(K.cast(y_true*y_pred, 'float'), axis=0)
		tn = K.sum(K.cast((1-y_true)*(1-y_pred), 'float'), axis=0)
		fp = K.sum(K.cast((1-y_true)*y_pred, 'float'), axis=0)
		fn = K.sum(K.cast(y_true*(1-y_pred), 'float'), axis=0)

		p = tp / (tp + fp + K.epsilon())
		r = tp / (tp + fn + K.epsilon())

		f1 = (1+beta**2) *p*r / ((beta**2)*p+r+K.epsilon())
		f1 = tf.where(tf.math.is_nan(f1), tf.zeros_like(f1), f1)
		return 1 - K.mean(f1)

	best_val_f1 = 0
	patience = 0
	input_x = Input(shape=(104,))
	hidden = Dense(300, activation='sigmoid')(input_x)
	dropout = Dropout(0.5)(hidden)

#	 output = Dense(1, activation='sigmoid')(dropout)
	output = Dense(1, activation='sigmoid')(dropout)
	model = Model(input_x, output)
	model.compile(Adam(lr=1e-3), loss=f1_loss,metrics=['accuracy'])

	positive_ids = np.where(labels==1)[0]
	positive_dt = dt[positive_ids, :]
	positive_labels = labels[positive_ids]

	for learnIter in range(20):
		print('learning iteration: ', learnIter)
		negative_ids = np.where(labels==0)[0]
		random_sampled_negative_ids = np.random.choice(negative_ids, size=positive_ids.shape[0]*2, replace=False)
		
		negative_dt = dt[random_sampled_negative_ids, :]

		negative_labels = labels[random_sampled_negative_ids]

		epoch_dt = np.concatenate((positive_dt, negative_dt))
		epoch_labels = np.concatenate((positive_labels, negative_labels))
		# print('epoch sample num: ', epoch_labels.shape[0], ' positive: ', positive_dt.shape[0], ' negative: ', negative_dt.shape[0])

		model.fit(epoch_dt, epoch_labels, batch_size=10, epochs=20, verbose=0)

	# Current version
	dfCV0 = readData(projectName, versionNum)
	dfCV = dfCV0.iloc[:, 2:-3]

	start_time = time.time()

	dfCV[criteria.index[criteria]] = np.log(1+dfCV[criteria.index[criteria]].values)

	dtCV = transform.transform(dfCV)
	predictedLabels = np.asarray(model.predict(dtCV), dtype=np.float64)[:,0]
	trueLabels = np.asarray(dfCV0.is_buggy, dtype=np.float64)

	elapsed_time = time.time() - start_time

	print("elapsed_time: ",elapsed_time)
	# print(predictedLabels)
	# print(trueLabels)
	print('mean all prediction labels: ', np.mean(predictedLabels))

	meanTpLabels = np.sum(np.dot(predictedLabels, trueLabels))/np.sum(trueLabels)
	print('mean true positive lalels: ', meanTpLabels)

	predictionResults = np.hstack([predictedLabels.reshape(-1,1),np.array(dfCV0.ClassLongName).reshape(-1,1)])

	outputFileName='%s/%s/%d/nn_bugprediction.csv' % (dataPath, projectName, versionNum)

	np.savetxt(outputFileName, predictionResults, delimiter=",", header="bugpred,LongName", fmt='%s', comments='')
	return elapsed_time