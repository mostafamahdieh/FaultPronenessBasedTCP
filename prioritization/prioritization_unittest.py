import numpy
import prioritization_core as pc

coverage = numpy.genfromtxt('coverage.csv', delimiter=';', dtype='float32')
print("coverage: \n", coverage)
testNum = coverage.shape[0]
unitNum = coverage.shape[1]
unitProb = numpy.ones((unitNum, ))
print("unitProb: ", unitProb)
failedIds = numpy.array([3, 4])
print("failedIds: ", failedIds)


additionalPrioritization = pc.additionalPrioritization(coverage, unitProb)
print("additionalPrioritization: ", additionalPrioritization, " APFD: ", pc.rankEvaluation(additionalPrioritization, failedIds))

totalPrioritization = pc.totalPrioritization(coverage, unitProb)
print("totalPrioritization: ", totalPrioritization, " APFD: ", pc.rankEvaluation(totalPrioritization, failedIds))

maxPrioritization = pc.maxPrioritization(coverage, unitProb)
print("maxPrioritization: ", maxPrioritization, " APFD: ", pc.rankEvaluation(maxPrioritization, failedIds))