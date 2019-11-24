# Introduction
Test case prioritization methods aim to benefit testing of a software (specifically regression testing), by prioritizing test cases in an order that minimizes the expected time of executing failing test cases. This project contains a test case prioritization method, based on defect prediction.

# Usage
- Get the code:
    ```
    git clone https://github.com/mostafamahdieh/DefectPredictionTCP.git
    ```
- Get the [Defects4J+M](https://github.com/khesoem/Defects4J-Plus-M) repository in the same directory:
    ```
    git clone https://github.com/khesoem/Defects4J-Plus-M.git
    ```
This package is used in two steps: defect prediction and priortization.

## Defect prediction
    cd bugprediction
    python -u bugprediction_runner.py

## Test case priortization
    cd priortization
    python -u prioritization_runner.py

## Citing in academic work
If you are using this dataset for your research, we would be really glad if you cite our paper using the following bibtex:
```
@article{mahdieh2019incorporating,
	Author = {Mostafa Mahdieh and Seyed-Hassan Mirian-Hosseinabadi and Khashayar Etemadi and Ali Nosrati and Sajad Jalali},
	Title = {Incorporating fault-proneness estimations into coverage-based test case prioritization methods},
	journal={arXiv preprint arXiv:1908.06502},
	Year = {2019}
}
```
