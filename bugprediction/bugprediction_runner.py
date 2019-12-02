#!/usr/bin/env python
# coding: utf-8

#get_ipython().run_line_magic('matplotlib', 'inline')
import keras_bugprediction
import time

projects = ['Chart', 'Closure', 'Lang', 'Math', 'Time']
fromVersion = [1, 1, 1, 1, 1]
toVersion = [13, 50, 33, 50, 14]
lastVersions = [26, 133, 65, 106, 27]


file = open("../../WTP-data/bugprediction_exectime.txt","a")
for index, project in enumerate(projects):
	print('*** Project: %s ***' % project)
	lastVersion = lastVersions[index]
	start_time = time.time()
	for version in range(fromVersion[index], toVersion[index]+1):
		print('Version: %d' % version)
		keras_bugprediction.kerasBugPrediction(project, version, lastVersion)
	elapsed_time = time.time() - start_time
	print("elapsed_time: ", elapsed_time)
	meanElapsedTime = elapsed_time/(toVersion[index]-fromVersion[index]+1)
	file.write("%s,%f\n" % (project, meanElapsedTime))
file.close()
