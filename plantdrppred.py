##############################################################################
#PlantDRPpred is developed for predicting Disease Resistance      #
#Proteins from their primary sequence. It is developed by Prof G. P. S.       #
#Raghava's group. Please cite : PlantDRPpred                                  #
# ############################################################################
import argparse  
import warnings
import pickle
import os
import re
import sys
import pandas as pd
import numpy as np
import glob
from Bio import SeqIO
import shutil
import zipfile
import requests

warnings.filterwarnings('ignore')
parser = argparse.ArgumentParser(description='Please provide following arguments. Please make the suitable changes in the envfile provided in the folder.') 

## Read Arguments from command
parser.add_argument("-i", "--input", type=str, required=True, help="Input: protein or peptide sequence in FASTA format")
parser.add_argument("-o", "--output",type=str, default="outfile.csv", help="Output: File for saving results by default outfile.csv")
parser.add_argument("-t","--threshold", type=float, default=0.5, help="Threshold: Value between 0 to 1 by default 0.48")
parser.add_argument("-m","--model",type=int, default=2, choices = [1, 2], help="Model: 1: AAC feature based ExtraTrees Classifier , 2: AAC + PSSM feature based ExtraTrees Classifier, by default 1")
parser.add_argument("-d","--display", type=int, choices = [1,2], default=2, help="Display: 1:AFP, 2: All peptides, by default 2")
parser.add_argument("-wd", "--working",type=str, default='.', help="Working Directory: Temporary directory to write files")

args = parser.parse_args()

nf_path = os.path.dirname(__file__)
#nf_path = os.getcwd()
std = list("ACDEFGHIKLMNPQRSTVWY")

def fasta_to_dataframe(fasta_file):
    sequences = {'ID': [], 'Sequence': []}
    
    # Parse the FASTA file
    for record in SeqIO.parse(fasta_file, 'fasta'):
        sequence_id = record.id.lstrip('>')  # Remove '>' from the ID
        sequences['ID'].append(sequence_id)
        sequences['Sequence'].append(str(record.seq))
    
    # Convert to DataFrame
    df = pd.DataFrame(sequences)
    
    return df


if not os.path.exists(nf_path + '/swissprot'):
    response = requests.get('https://webs.iiitd.edu.in/raghava/plantdrppred/swissprot.zip')
    if response.status_code == 200:
        with open(os.path.join(nf_path + '/swissprot.zip'), 'wb') as f:
                f.write(response.content)
    with zipfile.ZipFile(nf_path + '/swissprot.zip', 'r') as zip_ref:
            zip_ref.extractall(nf_path + '/' )
    print("ZIP file contents extracted successfully.")
    os.remove(nf_path + '/swissprot.zip')




def aac_comp(file,out):
    filename, file_extension = os.path.splitext(file)
    f = open(out, 'w')
    sys.stdout = f
    df = fasta_to_dataframe(file)
    zz = df['Sequence']
    print("AAC_A,AAC_C,AAC_D,AAC_E,AAC_F,AAC_G,AAC_H,AAC_I,AAC_K,AAC_L,AAC_M,AAC_N,AAC_P,AAC_Q,AAC_R,AAC_S,AAC_T,AAC_V,AAC_W,AAC_Y,")
    for j in zz:
        for i in std:
            count = 0
            for k in j:
                temp1 = k
                if temp1 == i:
                    count += 1
                composition = (count/len(j))*100
            print("%.2f"%composition, end = ",")
        print("")
    f.close()
    sys.stdout = sys.__stdout__

def BLAST_processor(blast_result,ml_results,thresh):
    if os.stat(blast_result).st_size != 0:
        df1 = pd.read_csv(blast_result, sep="\t", names=['name','hit','identity','r1','r2','r3','r4','r5','r6','r7','r8','r9'])
        df2 = ml_results
        #print(df2.head())
        cc = []
        for i in df2['ID']:
            kk = i.replace('>','')
            if len(df1.loc[df1.name==kk])>0:
                df4 = df1[['name','hit']].loc[df1['name']==kk].reset_index(drop=True)
                if df4['hit'][0].split('_')[0]=='P':
                    cc.append(0.5)
                if df4['hit'][0].split('_')[0]=='N':
                    cc.append(-0.5)
            else:
                cc.append(0)
        df6 = pd.DataFrame()
        df6['ID'] = [i.replace('>','') for i in df2['ID']]
        df6['ML Score'] = df2['ML Score']
        df6['BLAST Score'] = cc
        df6['Hybrid Score'] = df6['ML Score']+df6['BLAST Score']
        df6['Prediction'] = ['PDR' if df6['Hybrid Score'][i]>thresh else 'non-PDR' for i in range(0,len(df6))]
    else:
        df2 = ml_results
        ss = []
        vv = []
        for j in df2['ID']:
            ss.append(j.replace('>',''))
            vv.append(0)
        df6 = pd.DataFrame()
        df6['ID'] = ss
        df6['ML Score'] = df2['ML Score']
        df6['BLAST Score'] = vv
        df6['Hybrid Score'] = df6['ML Score']+df6['BLAST Score']
        df6['Prediction'] = ['PDR' if df6['Hybrid Score'][i]>thresh else 'non-PDR' for i in range(0,len(df6))]
    return df6



def readseq(file):
    with open(file) as f:
        records = f.read()
    records = records.split('>')[1:]
    seqid = []
    seq = []
    for fasta in records:
        array = fasta.split('\n')
        name, sequence = array[0].split()[0], re.sub('[^ACDEFGHIKLMNPQRSTVWY-]', '', ''.join(array[1:]).upper())
        seqid.append('>'+name)
        seq.append(sequence)
    if len(seqid) == 0:
        f=open(file,"r")
        data1 = f.readlines()
        for each in data1:
            seq.append(each.replace('\n',''))
        for i in range (1,len(seq)+1):
            seqid.append(">Seq_"+str(i))

    final_df = pd.concat([pd.DataFrame(seqid),pd.DataFrame(seq)], axis=1)
    final_df.columns = ['ID','Seq']
    return final_df

def file_split(file,path):
    df1 = readseq(file)
    for i in range(len(df1)):
        df1.loc[i].to_csv(path+'/'+df1['ID'][i].replace('>','')+'.fasta', index=None,header=False,sep="\n")

def gen_pssm(fasta_path, pssm_path):
    os.makedirs(pssm_path+'/pssm_raw1', exist_ok = True)
    os.makedirs(pssm_path+'/pssm_raw', exist_ok = True)

    listdir = glob.glob(fasta_path+'/*.fasta')
    for i in listdir:
        filename = i.split('/')[-1].rsplit('.', 1)[0]
        cmd = nf_path + "/ncbi_blast_2.15/bin/psiblast -out "+pssm_path+"/pssm_raw1/"+filename+".homologs -outfmt 7 -query "+fasta_path+"/"+filename+".fasta -db " + nf_path +  "/swissprot/swissprot -evalue 0.001 -word_size 3 -max_target_seqs 6000 -num_threads 10 -gapopen 11 -gapextend 1 -matrix BLOSUM62 -comp_based_stats T -num_iterations 3 -out_pssm "+pssm_path+"/pssm_raw1/"+filename+".cptpssm -out_ascii_pssm "+pssm_path+"/pssm_raw/"+filename+".pssm"
        os.system(cmd)

def feat_gen_aac(file,out):
    aac_comp(file, wd + '/aac_temp')
    df = pd.read_csv(wd + '/aac_temp')
    df = df.iloc[:,:-1]
    df.to_csv(out, index=None)
    os.remove(wd + '/aac_temp')

def feat_gen_pssm(file, out1, out2):
    feat_gen_aac(file, out1)
    aac_df = pd.read_csv(out1)
    file_split(file, wd + '/fasta_files')
    gen_pssm(wd + '/fasta_files', wd + '/pssm_files')
    df = fasta_to_dataframe(file)
    aac_df['ID'] = df['ID']
    aac_df.to_csv(out1, index=None)
    folder_path = wd + '/pssm_files/pssm_raw/'
    # List all items in the folder
    folder_items = os.listdir(folder_path)    
    if (len(folder_items)!=0):
        df.to_csv(wd + '/df')
        df1 = pd.DataFrame({'ID': folder_items})
        df1['ID'] = df1['ID'].str.replace('.pssm', '')
        df1.to_csv(wd + '/df1')
        pssm1 = pd.merge(df1, df, on="ID", how="left")
        pssm1['ID'] = '>' + pssm1['ID']
        pssm1[['ID','Sequence']].to_csv(wd + '/pssm_input.fasta' ,index= None, header=False, sep="\n")
        os.system('python3 ' + nf_path + '/possum/possum.py -i ' + wd + '/pssm_input.fasta' + ' -o ' + wd + '/pssm_temp1 -t pssm_composition -p ' + wd + '/pssm_files/pssm_raw')
        os.system('python3 ' + nf_path + '/possum/headerHandler.py -i ' + wd + '/pssm_temp1' + ' -o ' + wd + '/pssm_temp2 -p pssm_')
        df2 = pd.read_csv(wd + '/pssm_temp2')

        df2['ID'] = df1['ID']
        columns = list(df2.columns)
        columns.remove('ID')
        columns.append('ID')
        df2 = df2[columns]
        df2.to_csv(out2)
        os.remove(wd + '/pssm_input.fasta')
        os.remove(wd + '/pssm_temp1')
        os.remove(wd + '/pssm_temp2')



def prediction_aac(inputfile1, model,out):
    a=[]
    file_name = inputfile1
    file_name1 = out
    file_name2 = model
    with open(file_name2, 'rb') as file:
        clf1 = pickle.load(file)      
    data_test1 = pd.read_csv(inputfile1)    
    X_test = data_test1
    y_p_score1=clf1.predict_proba(X_test)
    y_p_s1=y_p_score1.tolist()
    df_dict = {'ML Score' : pd.DataFrame(y_p_s1).iloc[:,1]}
    df_1 = pd.DataFrame(df_dict)
    df_1.to_csv(file_name1, index=None)

def prediction_pssm(inputfile1, inputfile2, model1, model2, out):
    a=[]
    with open(model1, 'rb') as file:
        clf1 = pickle.load(file)    
    with open(model2, 'rb') as file:
        clf2 = pickle.load(file)   
    
    if (os.path.isfile(inputfile2)):

        data_test1 = pd.read_csv(inputfile1)
        data_test2 = pd.read_csv(inputfile2, index_col=0)

        X_test1 = np.array(data_test1.iloc[:,:-1])
        X_test2 = np.array(data_test2.iloc[:,:-1])
        y_p_score1=clf1.predict_proba(X_test1)
        y_p_score2=clf2.predict_proba(X_test2)

        y_p_s1=y_p_score1.tolist()
        y_p_s2=y_p_score2.tolist()

        df_dict1 = {'ML Score' : pd.DataFrame(y_p_s1).iloc[:,1], 'ID' : list(data_test1.iloc[:,-1])}
        df_1 = pd.DataFrame(data=df_dict1)

        df_dict2 = {'ML Score' : pd.DataFrame(y_p_s2).iloc[:,1], 'ID' : list(data_test2.iloc[:,-1])}
        df_2 = pd.DataFrame(data=df_dict2)

        merged_df = pd.merge(df_1, df_2, on='ID', suffixes=('_aac', '_pssm'), how='left')
        merged_df['ML Score_aac'] = merged_df['ML Score_pssm'].fillna(merged_df['ML Score_aac'])
        merged_df.drop(columns=['ML Score_pssm'], inplace=True)
        merged_df.rename(columns={'ML Score_aac': 'ML Score'}, inplace=True) 
        merged_df.to_csv(out, index=None)

    else:
        data_test1 = pd.read_csv(inputfile1)
        X_test1 = np.array(data_test1.iloc[:,:-1])
        y_p_score1=clf1.predict_proba(X_test1)
        y_p_s1=y_p_score1.tolist()
        df_dict1 = {'ML Score' : pd.DataFrame(y_p_s1).iloc[:,1]}
        df_1 = pd.DataFrame(data=df_dict1)
        df_1.to_csv(out, index=None)


def class_assignment(file1, thr, out):
    df1 = pd.read_csv(file1)
    cc = []
    for i in range(0,len(df1)):
        if df1['ML Score'][i]>=float(thr):
            cc.append('PDR')
        else:
            cc.append('Non-PDR')
    df1['Prediction'] = cc
    # df1 =  df1.round(3)
    df1.to_csv(out, index=None)

def class_assignment_blast(file, thr, out):
    pred_df = pd.read_csv(file)
    df1 = BLAST_processor(wd+'/RES_1_6_6.out',pred_df, thr)
    #print(df1.head())
    df1.to_csv(out, index=None)

print('##############################################################################')
print('# The program PlantDRPpred is developed for predicting PDR and non-PDR proteins #')
print("# from their primary sequence, developed by Prof G. P. S. Raghava's group. #")
print('# ############################################################################')

# Parameter initialization or assigning variable for command level arguments

Sequence= args.input        # Input variable 
 
# Output file 
result_filename = args.output
         
# Threshold 
Threshold= float(args.threshold)

# Model
Model = int(args.model)

# Display
dplay = int(args.display)

# Working Directory
wd = args.working

print('Summary of Parameters:')
print('Input File: ',Sequence,'; Model: ',Model,'; Threshold: ', Threshold)
print('Output File: ',result_filename,'; Display: ',dplay)

#------------------ Read input file ---------------------
f=open(Sequence,"r")
len1 = f.read().count('>')
f.close()

with open(Sequence) as f:
        records = f.read()
records = records.split('>')[1:]
seqid = []
seq = []
for fasta in records:
    array = fasta.split('\n')
    name, sequence = array[0].split()[0], re.sub('[^ARNDCQEGHILKMFPSTWYV-]', '', ''.join(array[1:]).upper())
    seqid.append(name)
    seq.append(sequence)
if len(seqid) == 0:
    f=open(Sequence,"r")
    data1 = f.readlines()
    for each in data1:
        seq.append(each.replace('\n',''))
    for i in range (1,len(seq)+1):
        seqid.append("Seq_"+str(i))

seqid_1 = list(map(">{}".format, seqid))

#======================= Prediction Module start from here =====================
if Model==1:
    os.makedirs(wd + '/fasta_files', exist_ok=True)
    os.makedirs(wd + '/pssm_files', exist_ok=True)
    feat_gen_pssm(Sequence, wd + '/seq.aac', wd + '/seq.pssm')
    prediction_pssm(wd + '/seq.aac', wd + '/seq.pssm', nf_path + '/model/model_aac', nf_path + '/model/model_pssm', wd + '/seq.pred')
    class_assignment(wd +'/seq.pred',Threshold, wd + '/seq.out')
    df1 = pd.DataFrame(seqid)
    df2 = pd.DataFrame(seq)
    df3 = pd.read_csv(wd + "/seq.out")
    df3 = round(df3,3)
    df4 = pd.concat([df1,df2,df3],axis=1)
    df4 = df4.drop(columns=['ID'])
    df4.columns = ['ID','Sequence','ML Score','Prediction']
    if dplay == 1:
        df4 = df4.loc[df4.Prediction=="PDR"]
    df4.to_csv(result_filename, index=None)
    os.remove(wd + '/seq.aac')
    os.remove(wd + '/seq.pred')
    os.remove(wd + '/seq.out')
else:
    os.makedirs(wd + '/fasta_files', exist_ok=True)
    os.makedirs(wd + '/pssm_files', exist_ok=True)
    feat_gen_pssm(Sequence, wd + '/seq.aac', wd + '/seq.pssm')
    prediction_pssm(wd + '/seq.aac', wd + '/seq.pssm', nf_path + '/model/model_aac', nf_path + '/model/model_pssm', wd + '/seq.pred')
    os.system(nf_path + '/ncbi_blast_2.15/bin/blastp -query ' + Sequence +  ' -db ' + nf_path +  '/blastdb/train -out ' + wd + '/RES_1_6_6.out -outfmt 6 -evalue 0.01' )
    class_assignment_blast(wd +'/seq.pred', Threshold, wd + '/seq.out')
    df1 = pd.DataFrame(seqid)
    df2 = pd.DataFrame(seq)
    df3 = pd.read_csv(wd + "/seq.out")
    df3 = round(df3,3)
    df3 = df3.iloc[:,-4:]
    df4 = pd.concat([df1,df2,df3],axis=1)
    df4.columns = ['ID','Sequence','ML Score','Blast Score', 'Hybrid Score', 'Prediction']
    df4.loc[df4['Hybrid Score'] > 1, 'Hybrid Score'] = 1
    df4.loc[df4['Hybrid Score'] < 0, 'Hybrid Score'] = 0
    if dplay == 1:
        df4 = df4.loc[df4.Prediction=="PDR"]
    df4.to_csv(result_filename, index=None)
    os.remove(wd + '/seq.aac')
    os.remove(wd + '/seq.pssm')
    os.remove(wd + '/seq.pred')
    os.remove(wd + '/seq.out')
    shutil.rmtree(wd + '/fasta_files')
    shutil.rmtree(wd + '/pssm_files')

print('\n======= Thanks for using PlantDRPpred. Your results are stored in file :',result_filename,' =====\n\n')
print('Please cite: PlantDRPpred\n')
