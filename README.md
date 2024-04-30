# PlantDRPpred
A method for prediction plant resistance protein

# Introduction
plantDRPpred is developed for predicting, mapping and scanning plant resistances proteins . More information on prrpred is available from its web server http://webs.iiitd.edu.in/raghava/plantDRPpred. This page provide information about standalone version of plantDRPpred.

## PIP Installation
PIP version is also available for easy installation and usage of this tool. The following command is required to install the package 
```
pip install plantDRPpred
```
To know about the available option for the pip package, type the following command:
```
plantDRPpred -h
```

# Standalone

Standalone version of plantDRPpred is written in python3 and the following libraries are necessary for a successful run:

- scikit-learn
- Pandas
- Numpy
- blastp

# Important Note

- Due to large size of the model file, we have not included it in the zipped folder or GitHub repository, thus to run standalone successfully you need to download model file and then unzip them.
- Make sure you extract the downloaded zip file in the directory where main execution file i.e. package.py is available.
- To download the model file click [here].(https://webs.iiitd.edu.in/raghava/plantdrppred/svc_model.zip)

**Minimum USAGE** 

To know about the available option for the standalone, type the following command:
```
package.py -h
```
To run the example, type the following command:
```
package.py -i seq.fasta

```
where seq.fasta is a input FASTA file. This will predict plant resistances protein in FASTA format. It will use other parameters by default. It will save output in "output_result.csv" in CSV (comma separated variables).

**Full Usage**: 
```
Following is complete list of all options, you may get these options
usage: toxinpred2.py [-h] 
                     [-i INPUT]
                     [-o OUTPUT]
                     [-m {1,2}] 
```
```
Please provide following arguments

optional arguments:

  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input: protein or peptide sequence in FASTA format or
                        single sequence per line in single letter code
  -o OUTPUT, --output OUTPUT
                        Output: File for saving results by default outfile.csv
  -m {1,2}, -- model Model
                        Model: 1: AAC based SVC, 2: PSSM based ET

```

**Input File**: It allow users to provide input in two format; i) FASTA format (standard) (e.g. seq.fasta)  

**Output File**: Program will save result in CSV format, in case user do not provide output file name, it will be stored in output_result.csv.


**Models**: In this program, two models have been incorporated;  
  i) Model1 for predicting given input protein sequence as R protein and non-R proteins  using SVC based on amino-acid composition of the proteins; 

  ii) Model2 for predicting given input peptide/protein sequence as R proteins and non-R protein using Hybrid approach, which is the ensemble of ET + BLAST. It combines the scores generated from machine learning (ET), and BLAST as Hybrid Score, and the prediction is based on Hybrid Score.


PlantDRPpred Package Files
=======================
It contain following files, brief description of these files given below

INSTALLATION  	: Installation instructions

LICENSE       	: License information

envfile : This file provide the path information for BLAST and MERCI commands ,and data 
          required to run BLAST and MERCI

Database: This folder contains the blast database

progs : This folder contains the program to run MERCI

README.md     	: This file provide information about this package

package.py 	: Main python program 

svc_model        : Model file required for running Machine-learning model

seq.fasta	: Example file contain peptide sequences in FASTA format



# Reference
.</a>
