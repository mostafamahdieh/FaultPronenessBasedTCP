import prioritization as pr
import time

alphaRangeNum = 5
projects = ['Chart', 'Closure', 'Lang', 'Math', 'Time']
fromVersion = [1, 1, 1, 1, 1]
toVersion = [13, 50, 33, 50, 14]

#projects = ['Chart']
#fromVersion = [1]
#toVersion = [13]

file = open("../../WTP-data/prioritization_exectime.txt","a")
for index, project in enumerate(projects):
	print('*** Project: %s ***' % project)
	for versionNumber in range(fromVersion[index], toVersion[index]+1):
		print("* Version %d" % versionNumber)
		start_time = time.time()
		pr.runPrioritization(project, versionNumber, alphaRangeNum)
		print()
	elapsed_time = time.time() - start_time
	print("elapsed_time: ", elapsed_time)
	meanElapsedTime = elapsed_time/(toVersion[index]-fromVersion[index]+1)
	file.write("%s,%f\n" % (project, meanElapsedTime))
file.close()
