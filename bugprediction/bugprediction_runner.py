#!/usr/bin/env python
# coding: utf-8

#get_ipython().run_line_magic('matplotlib', 'inline')
import keras_bugprediction

#projects = ['Math', 'Closure', 'Lang', 'Time', 'Chart']
#lastVersions = [106, 133, 65, 27, 26]
#fromVersion = [41, 41, 21, 11, 11]
#toVersion = [50, 50, 33, 14, 13]


projects = ['Lang']
lastVersions = [65]
fromVersion = [34]
toVersion = [50]


index = 0
for project in projects:
	print('*** Project: %s ***' % project)
	lastVersion = lastVersions[index]
	for version in range(fromVersion[index], toVersion[index]+1):
		print('Version: %d' % version)
		keras_bugprediction.kerasBugPrediction(project, version, lastVersion)
	index = index+1