# Introduction
Test case prioritization methods aim to benefit testing of a software (specifically regression testing), by prioritizing test cases in an order that minimizes the expected time of executing failing test cases. This project contains a test case prioritization method, based on defect prediction.

# Usage
## Prerequisites
- Get the code:
    ```
    git clone https://github.com/mostafamahdieh/DefectPredictionTCP.git
    ```
- Get the [Defects4J+M](https://github.com/khesoem/Defects4J-Plus-M) repository in the same directory:
    ```
    git clone https://github.com/khesoem/Defects4J-Plus-M.git
    ```
This package is used in multiple steps: defect prediction and prioritization.

## Defect prediction
The defect prediction step can be executed using the bugprediction_runner.py script as follows. This script runs the bug prediction step for the specific versions of all projects.
    cd bugprediction
    python -u bugprediction_runner.py

## Test case priortization
The prioritization_runner.py script is used to execute the traditional and fault-proneness based TCP methods. The total and additional strategies are executed in both the traditional and fault-proneness based methods.
    cd priortization
    python -u prioritization_runner.py

## Aggeragating the results
The results are aggregated using the aggregate_results.py script:
    cd results
    python -u aggregate_results.py

## Citing in academic work
If you are using this project for your research, we would be really glad if you cite our paper using the following bibtex:
```
@article{mahdieh2019incorporating,
	Author = {Mostafa Mahdieh and Seyed-Hassan Mirian-Hosseinabadi and Khashayar Etemadi and Ali Nosrati and Sajad Jalali},
	Title = {Incorporating fault-proneness estimations into coverage-based test case prioritization methods},
	journal={arXiv preprint arXiv:1908.06502},
	Year = {2019}
}
```
