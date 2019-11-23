import pandas as pd
import os
import matplotlib
import matplotlib.pyplot as plt
from numpy import std, mean, sqrt
import scipy.stats as stats

import itertools as it

from bisect import bisect_left
from typing import List

import numpy as np

from pandas import Categorical

def effectSize(lst1, lst2):
	return improvement(lst1, lst2)

def cliffsDelta(lst1, lst2, **dull):

    """Returns delta and true if there are more than 'dull' differences"""
    if not dull:
        dull = {'small': 0.147, 'medium': 0.33, 'large': 0.474} # effect sizes from (Hess and Kromrey, 2004)
    m, n = len(lst1), len(lst2)
    lst2 = sorted(lst2)
    j = more = less = 0
    for repeats, x in runs(sorted(lst1)):
        while j <= (n - 1) and lst2[j] < x:
            j += 1
        more += j*repeats
        while j <= (n - 1) and lst2[j] == x:
            j += 1
        less += (n - j)*repeats
    d = (more - less) / (m*n)
    size = lookup_size(d, dull)
    return d, size

def lookup_size(delta: float, dull: dict) -> str:
    """
    :type delta: float
    :type dull: dict, a dictionary of small, medium, large thresholds.
    """
    delta = abs(delta)
    if delta < dull['small']:
        return 'negligible'
    if dull['small'] <= delta < dull['medium']:
        return 'small'
    if dull['medium'] <= delta < dull['large']:
        return 'medium'
    if delta >= dull['large']:
        return 'large'


def runs(lst):
    """Iterator, chunks repeated values"""
    for j, two in enumerate(lst):
        if j == 0:
            one, i = two, 0
        if one != two:
            yield j - i, one
            i = j
        one = two
    yield j - i + 1, two

def odds_ratio(x,y):
	n = len(x)
	a = sum(x>y)
	b = n-a
	p = 0.01
	psi = ((a+p)/(n+p-a))/((b+p)/(n-p-b))
	return psi

def improvement(x,y):
	n = len(x)
	a = 0
	for i in range(0,n):
		a = a + x[i]/y[i]
	improvement = (a/n - 1)*100
	return improvement

def cohen_d(x,y):
    nx = len(x)
    ny = len(y)
    dof = nx + ny - 2
    return (mean(x) - mean(y)) / sqrt(((nx-1)*std(x, ddof=1) ** 2 + (ny-1)*std(y, ddof=1) ** 2) / dof)


def VD_A(treatment: List[float], control: List[float]):
    """
    Computes Vargha and Delaney A index
    A. Vargha and H. D. Delaney.
    A critique and improvement of the CL common language
    effect size statistics of McGraw and Wong.
    Journal of Educational and Behavioral Statistics, 25(2):101-132, 2000

    The formula to compute A has been transformed to minimize accuracy errors
    See: http://mtorchiano.wordpress.com/2014/05/19/effect-size-of-r-precision/

    :param treatment: a numeric list
    :param control: another numeric list

    :returns the value estimate and the magnitude
    """
    m = len(treatment)
    n = len(control)

    if m != n:
        raise ValueError("Data d and f must have the same length")

    r = stats.rankdata(treatment.append(control))

    r1 = sum(r[0:m])

    # Compute the measure
    # A = (r1/m - (m+1)/2)/n # formula (14) in Vargha and Delaney, 2000
    A = (2.0 * r1 - m * (m + 1)) / (2.0 * n * m)  # equivalent formula to avoid accuracy errors

    levels = [0.147, 0.33, 0.474]  # effect sizes from Hess and Kromrey, 2004
    magnitude = ["negligible", "small", "medium", "large"]
    scaled_A = (A - 0.5) * 2

    magnitude = magnitude[bisect_left(levels, abs(scaled_A))]
    estimate = A

    return estimate, magnitude


projects = ['Chart', 'Closure', 'Lang', 'Math', 'Time']
fromVersion = [1, 1, 1, 1, 1]
toVersion = [13, 50, 33, 50, 14]

matplotlib.rcParams.update({'font.size': 14})

pd.set_option('display.max_columns', 1000)

def readResults(fileName, fromVersion, toVersion):
	versionsSummed = 0

	versions = pd.Series()
	dataValsDp = pd.DataFrame()
	dataValsStd = pd.DataFrame()

	for versionNumber in range(fromVersion, toVersion):
		dataPath = "../../WTP-data/%s/%d" % (project, versionNumber)
		filePath = '%s/%s' % (dataPath, fileName)
		if (os.path.isfile(filePath)):
			print("Reading %s" % filePath)
			results = pd.read_csv(filePath, delimiter=',')
			
			if versionsSummed==0:
				dataValsMean = results
			else:
				dataValsMean = dataValsMean + results

			versions = versions.append(pd.Series([versionNumber]), ignore_index=True)
			dataValsStd = dataValsStd.append(results[results.C_dp==0.0])
			dataValsDp = dataValsDp.append(results[results.C_dp==0.7])


			versionsSummed = versionsSummed+1
		else:
			print("Skipping %s" % filePath)

	dataValsMean = dataValsMean / versionsSummed
	#print(dataValsMean)
	dataValsMean.to_csv('../../WTP-data/aggregate/%s.csv' % project, index=False)

	dataValsDp.index = range(0, dataValsDp.shape[0])
	dataValsStd.index = range(0, dataValsStd.shape[0])

#	print(ttest_ind(dataValsStd['additional'], dataValsStd['total']))

	dataValsDp.insert(0, 'version', versions)
	dataValsDp.insert(1, 'additional0', dataValsStd['additional'])
	dataValsDp.insert(2, 'total0', dataValsStd['total'])
	dataValsDp = dataValsDp.drop('C_dp', axis=1)
	return dataValsMean, dataValsDp


dataValsStats = pd.DataFrame()
effectSizeVals = pd.DataFrame(columns=['project','additional','total'])

for index, project in enumerate(projects):
	dataValsMean, dataValsDp = readResults('apfd.csv', fromVersion[index], toVersion[index]+1)
	dataValsStats = dataValsStats.append(dataValsDp.mean(), ignore_index=True)
#	dataValsStats = dataValsStats.append(dataValsDp.std(), ignore_index=True)
	dataValsDp.to_csv('../../WTP-data/aggregate/rqs/%s.apfd.aggregate.csv' % project, index=False)

	totalEffectSize = effectSize(dataValsDp["total"], dataValsDp["total0"])
	additionalEffectSize = effectSize(dataValsDp["additional"], dataValsDp["additional0"])
	print("effectSize total ", totalEffectSize)
	print("effectSize additional ", additionalEffectSize)
	effectSizeVals = effectSizeVals.append(pd.DataFrame({'project':[project],'total':[totalEffectSize],'additional':[additionalEffectSize]}), ignore_index=True, sort=False)
	
	if index == 0:
		dataValsAll = dataValsDp
	else:
		dataValsAll = dataValsAll.append(dataValsDp)


	dataValsDpForPlot = dataValsDp.rename(columns={"additional0": "Traditional", "additional": "Modified"})
	dataValsMeanForPlot = dataValsMean.rename(columns={"additional": "Modified Additional"})


#	print(aggregate_data)

	plt.close('all')
	plot1 = dataValsDpForPlot.boxplot(column=['Traditional', 'Modified'])
	plot1.set_ylabel('APFD (%)')
	plot1.set_ylim(0, 100)

	fig1 = plot1.get_figure()
#	fig1.suptitle(project, fontsize=20)
	fig1.savefig('../../WTP-data/aggregate/rqs/%s.additional.apfd.boxplot.png' % project)	

	plt.close('all')
	plot2 = dataValsMeanForPlot.plot(x='C_dp', y=['Modified Additional'], style='.-', grid=True, xlim=(0,1))	

	plot2.set_xlabel('C_dp (1-P0)')
	plot2.set_ylabel('APFD (%)')
	plot2.set_ylim(40, 80)

	fig2 = plot2.get_figure()
#	fig2.suptitle(project, fontsize=20)
	fig2.savefig('../../WTP-data/aggregate/rqs/%s.additional.apfd.plot.png' % project)


	dataValsDpForPlot = dataValsDp.rename(columns={"total0": "Traditional", "total": "Modified"})
	dataValsMeanForPlot = dataValsMean.rename(columns={"total": "Modified Total"})


	#	print(aggregate_data)

	plt.close('all')
	plot1 = dataValsDpForPlot.boxplot(column=['Traditional', 'Modified'])
	plot1.set_ylabel('APFD (%)')
	plot1.set_ylim(0, 100)

	fig1 = plot1.get_figure()
#	fig1.suptitle(project, fontsize=20)
	fig1.savefig('../../WTP-data/aggregate/rqs/%s.total.apfd.boxplot.png' % project)	

	plt.close('all')
	plot2 = dataValsMeanForPlot.plot(x='C_dp', y=['Modified Total'], style='.-', grid=True, xlim=(0,1))	

	plot2.set_xlabel('C_dp (1-P0)')
	plot2.set_ylabel('APFD (%)')
	plot2.set_ylim(40, 80)

	fig2 = plot2.get_figure()
#	fig2.suptitle(project, fontsize=20)
	fig2.savefig('../../WTP-data/aggregate/rqs/%s.total.apfd.plot.png' % project)

dataValsAll = dataValsAll.reset_index()

#dataValsSumOfAll = dataValsSumOfAll/len(projects)
#plot = dataValsSumOfAll.plot(x='C_dp')	
#fig = plot.get_figure()
#fig.savefig('../../WTP-data/aggregate/all.png')

#print("VD_A total ", VD_A(dataValsAll["total0"], dataValsAll["total"]))
#print("VD_A additional ", VD_A(dataValsAll["additional0"], dataValsAll["additional"]))
totalEffectSize = effectSize(dataValsAll["total"], dataValsAll["total0"])
additionalEffectSize = effectSize(dataValsAll["additional"], dataValsAll["additional0"])
print("effectSize total ", totalEffectSize)
print("effectSize additional ", additionalEffectSize)
effectSizeValsMean = effectSizeVals.mean()
effectSizeVals = effectSizeVals.append(pd.DataFrame({'project':['average'],'total':[effectSizeValsMean['total']],'additional':[effectSizeValsMean['additional']]}), ignore_index=True, sort=False)
effectSizeVals = effectSizeVals.append(pd.DataFrame({'project':['all'],'total':[totalEffectSize],'additional':[additionalEffectSize]}), ignore_index=True, sort=False)

print("additional wicoxon-text p-value:", stats.wilcoxon(dataValsAll["additional"],dataValsAll["additional0"]))
print("total wicoxon-text p-value:", stats.wilcoxon(dataValsAll["total"],dataValsAll["total0"]))
print("additional/total wicoxon-text p-value:", stats.wilcoxon(dataValsAll["additional0"],dataValsAll["total0"]))

dataValsAll = dataValsAll.append(dataValsAll.mean(), ignore_index=True)
dataValsAll.to_csv('../../WTP-data/aggregate/rqs/all.apfd.aggregate.csv', index=False)
dataValsStats.to_csv('../../WTP-data/aggregate/rqs/stats.apfd.aggregate.csv', index=False)

effectSizeVals.to_csv('../../WTP-data/aggregate/rqs/effectsize.apfd.csv', index=False)
