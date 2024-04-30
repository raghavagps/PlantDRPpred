import pandas as pd
import re
import sys
import os
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
file_split(sys.argv[1],sys.argv[2])
