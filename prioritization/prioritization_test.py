source("prioritization_core.r")
library(rhdf5)
runPrioritization = function(versionNumber) {
  #coverage <- read.csv(sprintf("../WTP-data/%s/%d/test_coverage.csv", project, versionNumber),check.names=FALSE,sep=",");
  bugpred  <- read.csv(sprintf("../WTP-data/%s/%d/bugpred.csv", project, versionNumber) ,sep=",");
  if (crossProject) {
    bugpredCrossProject  <- read.csv(sprintf("../WTP-data/%s/%d/bugpred_cross_%s.csv", project, versionNumber, trainProject) ,sep=",");
  }
  h5address <- sprintf("../WTP-data/%s/%d/TestCoverage.h5", project, versionNumber);
  dataSize <- as.numeric(h5ls(h5address)[1,5])
  readSeq <- c(seq(1,dataSize,1000),dataSize)
  testNames <- h5read(h5address, "columnTestNamesArray")
  unitNames <- h5read(h5address, "rowMethodNamesArray")
  coverage <- matrix(0, ncol = length(unitNames), nrow = length(testNames))
  #print(length(unitNames))
  #print(dim(coverage))
  #print(length(d))
  for( i in 1:length(readSeq)-1) {
	top <- readSeq[i+1]
	min <- readSeq[i]
	for(j in min:top){
  		d <- h5read(h5address, "data", index=list(min,top))
  		r <- h5read(h5address, "row", index=list(min,top))
  		c <- h5read(h5address, "column", index=list(min,top))
		coverage[r[j-min]+1,c[i-min]+1] = as.double(d[i-min])
	}
	
  }
#  coverage <- as.numeric(coverage) 

  failedTests <- scan(sprintf("../WTP-data/%s/%d/FailedTests.txt", project, versionNumber), what="", sep="\n")
  
  #testNames <- colnames(coverage)
  #testNames <- testNames[-1]
  
  #unitNames <- t(coverage[,1])
  #coverage <- t(coverage[,-1])
  #coverage <- as.matrix(read.csv("coverage.csv",sep=";"))
  
  failedTestsIds <- c()
  for (failedTest in failedTests) {
    w = which(testNames == failedTest)
    if (length(w) == 0) {
      #print(sprintf("test %s not found in coverage test names", failedTest))
    } else {
      failedTestsIds <- c(failedTestsIds, w[1])
    }
  }
  
  testNum <- dim(coverage)[1]
  unitNum <- dim(coverage)[2]
  print(unitNum)
  unitNamesStr <- rep("", unitNum)
  unitClassName <- rep("", unitNum)
  testClassName <- rep("", testNum)
  
  for (u in 1:unitNum) {
    unitNamesStr[u] <- toString(unitNames[u])
    s <- strsplit(unitNamesStr[u],"#")
    unitClassName[u] = s[[1]][1]
  }
  
  for (t in 1:testNum) {
    testNameStr <- toString(testNames[t])
    s <- strsplit(testNameStr,"#")
    testClassName[t] = s[[1]][1]
  }
  
  unitProbWeighted = rep(alpha, unitNum) + (1-alpha) * unitProbRetreive(bugpred, unitClassName)
  
  totalMethodRanks = totalPrioritization(coverage, rep(1.0, unitNum))
  scoreTotal = rankEvaluation(totalMethodRanks, failedTestsIds)
  print(sprintf("Total strategy score: %f", scoreTotal))

  totalMethodWeightedRanks = totalPrioritization(coverage, unitProbWeighted)
  scoreTotalWeighted = rankEvaluation(totalMethodWeightedRanks, failedTestsIds)
  print(sprintf("Total Weighted strategy score: %f", scoreTotalWeighted))
  
  additionalMethodRanks <- additionalPrioritization(coverage, rep(1.0, unitNum))
  scoreAdditional = rankEvaluation(additionalMethodRanks, failedTestsIds)
  print(sprintf("Additional method score: %f", scoreAdditional))
  
  additionalWeightedRanks <- additionalPrioritization(coverage, unitProbWeighted)
  scoreAdditionalWeighted = rankEvaluation(additionalWeightedRanks, failedTestsIds)
  print(sprintf("Additional Weighted method score: %f", scoreAdditionalWeighted))
  
  writeLines(sprintf('%f\n%f\n%f\n%f\n', scoreTotal, scoreAdditional, scoreTotalWeighted, scoreAdditionalWeighted), sprintf("../WTP-data/%s/%d/scores_%f.txt", project, versionNumber, alpha))
  
  maxMethodWeightedRanks = maxPrioritization(coverage, unitProbWeighted)
  scoreMaxWeighted = rankEvaluation(maxMethodWeightedRanks, failedTestsIds)
  print(sprintf("Max Weighted strategy score: %f", scoreMaxWeighted))
  
  maxByClassRanks = sort(testProbRetreive(testClassName, bugpred), decreasing = TRUE, index.return = TRUE)$ix
  scoreMaxByClass = rankEvaluation(maxByClassRanks, failedTestsIds)
  print(sprintf("Max By Class strategy score: %f", scoreMaxByClass))
  
  writeLines(sprintf('%f\n%f\n', scoreMaxWeighted, scoreMaxByClass), sprintf("../WTP-data/%s/%d/scores_experimental_%f.txt", project, versionNumber, alpha))
  
  if (crossProject) {
    unitProbWeightedCrossProject = rep(alpha, unitNum) + (1-alpha) *unitProbRetreive(bugpredCrossProject, unitClassName)
    
    totalMethodWeightedCrossProjectRanks = totalPrioritization(coverage, unitProbWeightedCrossProject)
    scoreTotalWeightedCrossProject = rankEvaluation(totalMethodWeightedCrossProjectRanks, failedTestsIds)
    print(sprintf("Total Weighted Cross Project strategy score: %f", scoreTotalWeightedCrossProject))
    
    additionalWeightedRanksCrossProject <- additionalPrioritization(coverage, unitProbWeightedCrossProject)
    scoreAdditionalWeightedCrossProject = rankEvaluation(additionalWeightedRanksCrossProject, failedTestsIds)
    print(sprintf("Additional Weighted Cross-project score: %f", scoreAdditionalWeighted))
  
    writeLines(sprintf('%f\n%f\n', scoreTotalWeightedCrossProject, scoreAdditionalWeightedCrossProject), sprintf("../WTP-data/%s/%d/scores_cross_%s_%f.txt", project, versionNumber, trainProject, alpha))
 
     maxMethodWeightedCrossProjectRanks = maxPrioritization(coverage, unitProbWeightedCrossProject)
    scoreMaxWeightedCrossProject = rankEvaluation(maxMethodWeightedCrossProjectRanks, failedTestsIds)
    print(sprintf("Max Weighted Cross Project strategy score: %f", scoreMaxWeightedCrossProject))
    
    maxByClassCrossProjectRanks = sort(testProbRetreive(testClassName, bugpredCrossProject), decreasing = TRUE, index.return = TRUE)$ix
    scoreMaxByClassCrossProject = rankEvaluation(maxByClassCrossProjectRanks, failedTestsIds)
    print(sprintf("Max By Class strategy Cross Project score: %f", scoreMaxByClassCrossProject))
  
    writeLines(sprintf('%f\n%f\n', scoreMaxWeightedCrossProject, scoreMaxByClassCrossProject), sprintf("../WTP-data/%s/%d/scores_experimental_cross_%s_%f.txt", project, versionNumber, trainProject, alpha))
  }
}
