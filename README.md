# **PlantDRPpred**
A computational method to predict the plant disease resistance protein based on evolutionary profiles. 
## Introduction
PlantDRPpred is a tool developed by Raghava-Lab in 2024. It is designed to predict whether a plant protein is Disease Resistant or not. It utilizes amino-acid compositions  with XGBoost Classifier and PSSM as features to make predictions using an Random Forest Classifier. PlantDRPpred is also available as web-server at https://webs.iiitd.edu.in/raghava/plantdrppred. Please read/cite the content about the PlantDRPpred for complete information including algorithm behind the approach.

## PIP Installation
PIP version is also available for easy installation and usage of this tool. The following command is required to install the package 
```
pip install plantdrppred
```
To know about the available option for the pip package, type the following command:
```
plantdrppred -h
```
# Standalone

Standalone version of PlantDRPpred is written in python3 and the following libraries are necessary for a successful run:

- scikit-learn = 1.3.2
- Pandas
- Numpy
- blastp


## Minimum USAGE
To know about the available option for the standalone, type the following command:
```
python plantdrppred.py -h
```
To run the example, type the following command:
```
python plantdrppred.py -i example_input.fasata
```
This will predict the probability whether a submitted sequence will PDR or non-PDR. It will use other parameters by default. It will save the output in "outfile.csv" in CSV (comma separated variables).

## Full Usage
```
usage: plantdrppred.py [-h] -i INPUT [-o OUTPUT] [-t THRESHOLD] [-m {1,2}] [-d {1,2}]
                    [-wd WORKING]
=======
```
To run the example, type the following command:
```
plantdrppred.py -i example_input.fasta

```
```
Please provide following arguments.
=======
Following is complete list of all options, you may get these options
usage: plantdrppred.py [-h] 
                     [-i INPUT]
                     [-o OUTPUT]
                     [-m {1,2}] 
```
```
Please provide following arguments

optional arguments:

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input: protein sequence in FASTA format
  -o OUTPUT, --output OUTPUT
                        Output: File for saving results by default outfile.csv
  -t THRESHOLD, --threshold THRESHOLD
                        Threshold: Value between 0 to 1 by default 0.50
  -m {1,2}, --model {1,2}
                        Model: 1: PSSM feature based Random Forest Classifier , 2:  PSSM
                        feature based Random Forest + BLAST , by default 1
  -d {1,2}, --display {1,2}
                        Display: 1: PDR, 2: All proteins, by default 2
  -wd WORKING, --working WORKING
                        Working Directory: Temporary directory to write files
```

**Input File:** It allow users to provide input in the FASTA format.

**Output File:** Program will save the results in the CSV format, in case user does not provide output file name, it will be stored in "outfile.csv".

**Threshold:** User should provide threshold between 0 and 1, by default its 0.5.

**Display type:** This option allow users to display only PDR proteins or all the input proteins.

**Working Directory:** Directory where intermediate files as well as final results will be saved

PlantDRPpred Package Files
=======================
It contains the following files, brief description of these files given below


LICENSE				      : License information

README.md			      : This file provide information about this package

blastdb             : The folder contain blast database of all sequences in dataset 

model               : This folder contains two pickled models

ncbi_blast_2.15     : This folder contains blast psiblast and blastp(for linux) 

plantdrppred.py     : Main python program

possum              : This folder contains the program POSSUM, that is used to calculate PSSM features

example_input.fasta : Example file containing protein sequences in FASTA format

example_output.csv	: Example output file for the program
