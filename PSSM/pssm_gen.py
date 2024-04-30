#Usage: python3 pssm_gen.py <Path of the directory>
import sys
import glob
import os
dir_path = sys.argv[1]
os.makedirs(dir_path+'/pssm_raw1', exist_ok = True)
os.makedirs(dir_path+'/pssm_raw', exist_ok = True)

listdir = glob.glob(dir_path+'/*.fasta')
for i in listdir:
    filename = i.split('/')[-1].split('.')[0]
    cmd = "PSSM/psiblast -out "+dir_path+"/pssm_raw1/"+filename+".homologs -outfmt 7 -query "+dir_path+"/"+filename+".fasta -db PSSM/Database/Uniprot_database -evalue 0.0001 -word_size 3 -max_target_seqs 6000 -num_threads 4 -gapopen 11 -gapextend 1 -matrix BLOSUM62 -comp_based_stats T -num_iterations 3 -out_pssm "+dir_path+"/pssm_raw1/"+filename+".cptpssm -out_ascii_pssm "+dir_path+"/pssm_raw/"+filename+".pssm"
    print(str(cmd))
    os.system(cmd)
