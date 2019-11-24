import prioritization as pr

alphaRangeNum = 5
projects = ['Chart', 'Closure', 'Math', 'Lang', 'Time']
fromVersion = [1, 1, 1, 1, 1]
toVersion = [13, 50, 50, 33, 14]

#projects = ['Chart']
#fromVersion = [1]
#toVersion = [13]

index = 0
for project in projects:
	for versionNumber in range(fromVersion[index], toVersion[index]+1):
		print("* Version %d" % versionNumber)
		pr.runPrioritization(project, versionNumber, alphaRangeNum)
		print()
	index = index+1	