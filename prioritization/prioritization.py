import numpy as np
import pandas as pd
import prioritization_core as pc
import h5py
import os.path
import zipfile
import time

def findRowIndex(data, value):
	for i in range(0, data.shape[0]):
		if (str(data[i]) == value):
			return i
	return -1

def runPrioritization(project, versionNumber, alphaRangeNum):
	dataPath = '../../WTP-data'
	projectDataPath = '%s/%s/%d' % (dataPath, project, versionNumber)

	bugpred = pd.read_csv('%s/nn_bugprediction.csv' % projectDataPath, delimiter=',')
#	bugpred = pd.read_csv('%s/bugpred.csv' % dataPath, delimiter=',')
	h5FileAddress = '%s/TestCoverage.h5' % projectDataPath

	zipFileName='%s/TestCoverage.zip' % (projectDataPath)

	if (not os.path.isfile(h5FileAddress) and os.path.isfile(zipFileName)):
		print("Unzipping ",zipFileName)
		with zipfile.ZipFile(zipFileName, 'r') as zip_ref:
			zip_ref.extractall(projectDataPath)	

	h5 = h5py.File(h5FileAddress)

	dataSize=h5["data"].shape[0]
	testNames = h5["columnTestNamesArray"]
	unitNames = h5["rowMethodNamesArray"]
	unitNum = unitNames.shape[0]
	testNum = testNames.shape[0]

	failedTestsFile = ("%s/FailedTests.txt" % projectDataPath)

	with open(failedTestsFile) as f:
	    failedTests = f.readlines()

	# you may also want to remove whitespace characters like `\n` at the end of each line
	failedTests = [x.strip() for x in failedTests] 

	failedTestsIds = list()

	for failedTest in failedTests:
		failedTestIndex = findRowIndex(testNames, "b'"+failedTest+"'")
		if failedTestIndex == -1:
		  print("Test %s not found in coverage test names" % failedTest)
		else:
		  failedTestsIds.append(failedTestIndex)

	if (np.size(failedTestsIds)==0):
		print("No Tests found in coverage values, skipping version")
		return	

	print("failedTestsIds: ", failedTestsIds)
	print("unitNum: ", unitNum)
	print("testNum: ", testNum)

	coverage = np.zeros(shape=(testNum,unitNum))
	readSeq = range(0, dataSize, 1000)

	print("Loading coverage from " + h5FileAddress + "...")
	for i in range(0, len(readSeq)):
	    floor = readSeq[i]
	    if i < len(readSeq)-1:
	        top = readSeq[i+1]
	    else:
	        top = dataSize-1

	    d = h5["data"][floor:top]
	    r = h5["row"][floor:top]
	    c = h5["column"][floor:top]
	    for j in range(floor,top):
	        coverage[r[j-floor]][c[j-floor]] = d[j-floor]

	f = open('%s/apfd.csv' % projectDataPath, "w+")
	f.write("C_dp,additional,total,max,max_normal\n")

	unitBugPred = np.zeros((unitNum, ))

	for u in range(0, unitNum):
		unitClass = str(unitNames[u])[2:].split('#')[0]
		unitClass = unitClass.strip()
		b = bugpred[bugpred.LongName==unitClass]
		if (not b.empty):
			unitBugPred[u] = b.bugpred

	for alphaIndex in range(0, alphaRangeNum+1):
		C_dp = float(alphaIndex)/float(alphaRangeNum)
		print("** running for C_dp: ", C_dp)

#		np.set_printoptions(threshold=np.nan)
		weightedUnitProb = (1-C_dp)*np.ones((unitNum, ))+C_dp*unitBugPred
#		print("weightedUnitProb: ", weightedUnitProb)

		additional_start_time = time.time()
		weightedAdditionalPrioritization = pc.additionalPrioritization(coverage, weightedUnitProb)
		additional_elapsed_time = additional_elapsed_time + time.time() - additional_start_time

		waAPFD = pc.rankEvaluation(weightedAdditionalPrioritization, failedTestsIds)
		print("weightedAdditionalPrioritization: ", waAPFD)

		total_start_time = time.time()
		weightedTotalPrioritization = pc.totalPrioritization(coverage, weightedUnitProb)
		total_elapsed_time = total_elapsed_time + time.time() - total_start_time

		wtAPFD = pc.rankEvaluation(weightedTotalPrioritization, failedTestsIds)
		print("weightedTotalPrioritization: ", wtAPFD)
		# weightedMaxPrioritization = pc.maxPrioritization(coverage, weightedUnitProb)
		# wmAPFD = pc.rankEvaluation(weightedMaxPrioritization, failedTestsIds)
		# print("weightedMaxPrioritization: ", wmAPFD)
		# weightedMaxNormalizedPrioritization = pc.maxNormalizedPrioritization(coverage, weightedUnitProb)
		# wmnAPFD = pc.rankEvaluation(weightedMaxNormalizedPrioritization, failedTestsIds)
		# print("weightedMaxNormalizedPrioritization: ", wmnAPFD)

		resultLine = "%f,%f,%f,%f,%f" % (C_dp, waAPFD, wtAPFD, 0, 0)
		f.write(resultLine+"\n")
		print()
	f.close()

	return (additional_elapsed_time/alphaRangeNum,total_elapsed_time/alphaRangeNum)
