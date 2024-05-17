####################################################################################################
# PlantDRPpred is developed for predicting, designing and scanning the Plant resistances proteins  #
#  It is developed by Prof G. P. S. Raghava's group.                                                #
# Please cite: https://webs.iiitd.edu.in/raghava/plantdrppred/                                      #
###################################################################################################

import os
import pandas as pd
import joblib
import argparse
import subprocess
import shutil
import sys
import glob
import re
import zipfile
import requests


def save_fasta_sequences(input_file):
    """
    Function to save FASTA sequences provided by the user to a file.
    """
    output_folder = "Fea_Seq"
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, "sequences.fasta")
    
    with open(input_file, 'r') as f:
        with open(output_file, 'w') as file:
            for line in f:
                file.write(line)  # Write the line as it is without any modification
    
    print("Input saved to", output_file)
    return output_file



def run_option_1(input_file, output_file="output_results.csv"):
    # Save FASTA sequences first
    save_fasta_sequences(input_file)  
    
    # Change directory to pfeature_standalone
    os.chdir("pfeature")
    # AAC feature extraction of the test file
    subprocess.run(["python3", "pfeature_comp.py", "-i", "../Fea_Seq/sequences.fasta", "-o", "../Fea_Seq/AAC_feature.csv", "-j", "AAC"])
    # Change back to the original directory
    os.chdir("..")
    # Load the SVC model with AAC
    loaded_model1 = joblib.load("Models/svc_model.pkl")
    feature = pd.read_csv("Fea_Seq/AAC_feature.csv")
    # Use the loaded model to make predictions on the test dataset
    y_pred_proba = loaded_model1.predict_proba(feature)[:, 1]

    # Read the FASTA file to extract sequence IDs (headers)
    with open(input_file, "r") as fasta_file:
        fasta_lines = fasta_file.readlines()
    headers = [line.strip()[1:] for line in fasta_lines if line.startswith(">")]

    # Create a DataFrame with sequence IDs and probabilities
    results_df = pd.DataFrame({"ID": headers, "ML_Score": y_pred_proba})

    # Save the DataFrame to a CSV file
    results_df.to_csv(output_file, index=False)
    print(f"Output of SVC with AAC saved to {output_file}")
    return y_pred_proba  # Return predicted probabilities






def save_sequences_in_output_files(fasta_file, folder_path, pssm_output_file, not_in_pssm_output_file):
    # Function to read sequences from a FASTA file
    def read_sequences(fasta_file):
        sequences = {}
        current_id = None
        with open(fasta_file, 'r') as f:
            for line in f:
                if line.startswith('>'):
                    current_id = line.strip()[1:]
                    sequences[current_id] = ''
                else:
                    sequences[current_id] += line.strip()
        return sequences

    # Get the list of file names in the folder
    file_list = [name.replace(".pssm", '') for name in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, name))]

    # Read sequences from the FASTA file
    fasta_sequences = read_sequences(fasta_file)

    # Filter out sequences present in both files
    sequences_in_pssm_raw = {seq_id: sequence for seq_id, sequence in fasta_sequences.items() if seq_id in file_list}
    sequences_not_in_pssm_raw = {seq_id: sequence for seq_id, sequence in fasta_sequences.items() if seq_id not in file_list}

    # Write the sequences present in pssm_raw folder to the output file
    with open(pssm_output_file, 'w') as f_out:
        for seq_id, sequence in sequences_in_pssm_raw.items():
            f_out.write(f">{seq_id}\n{sequence}\n")

    # print(f"Sequences in pssm_raw folder saved to {pssm_output_file}")

    # Write the sequences not present in pssm_raw folder to the output file
    with open(not_in_pssm_output_file, 'w') as f_out:
        for seq_id, sequence in sequences_not_in_pssm_raw.items():
            f_out.write(f">{seq_id}\n{sequence}\n")

    # print(f"Sequences not in pssm_raw folder saved to {not_in_pssm_output_file}")


def generate_pssm(dir_path):
    """
    Function to generate PSSM profiles for FASTA files in the specified directory.
    """
    # Create directories to store intermediate and final PSSM files
    os.makedirs(os.path.join(dir_path, 'pssm_raw1'), exist_ok=True)
    os.makedirs(os.path.join(dir_path, 'pssm_raw'), exist_ok=True)

    # Find all FASTA files in the specified directory
    listdir = glob.glob(os.path.join(dir_path, '*.fasta'))
    
    # Iterate over each FASTA file
    for i in listdir:
        # Extract filename without extension
        filename = os.path.splitext(os.path.basename(i))[0]
        
        # Construct PSI-BLAST command to generate PSSM profile
        cmd_psiblast = f"psiblast -out {os.path.join(dir_path, 'pssm_raw1', filename)}.homologs -outfmt 7 -query {i} -db swissprot/Uniprot_database -evalue 0.0001 -word_size 3 -max_target_seqs 6000 -num_threads 4 -gapopen 11 -gapextend 1 -matrix BLOSUM62 -comp_based_stats T -num_iterations 3 -out_pssm {os.path.join(dir_path, 'pssm_raw1', filename)}.cptpssm -out_ascii_pssm {os.path.join(dir_path, 'pssm_raw', filename)}.pssm"
        
        # Print and execute the PSI-BLAST command
        print(cmd_psiblast)
        os.system(cmd_psiblast)


# Check if the swissprot directory exists
if not os.path.exists(os.path.join(current_dir, 'swissprot')):
    # If it doesn't exist, download the SwissProt database ZIP file
    response = requests.get('https://webs.iiitd.edu.in/raghava/plantdrppred/swissprot.zip')
    if response.status_code == 200:
        # Write the downloaded ZIP file
        with open(os.path.join(current_dir, 'swissprot.zip'), 'wb') as f:
            f.write(response.content)
        
        # Extract the contents of the ZIP file
        with zipfile.ZipFile(os.path.join(current_dir, 'swissprot.zip'), 'r') as zip_ref:
            zip_ref.extractall(current_dir)
        
        # Remove the downloaded ZIP file
        os.remove(os.path.join(current_dir, 'swissprot.zip'))



# file_split function for PSSM
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


def process_blast_results(blast_result_file, results_df1):
    df1 = pd.read_csv(blast_result_file, sep="\t", names=['name','hit','identity','r1','r2','r3','r4','r5','r6','r7','r8','r9'])

    cc = []
    
    if os.stat(blast_result_file).st_size != 0: 
        for i in results_df1['ID']:
            if len(df1.loc[df1['name'] == i]) > 0:
                df4 = df1[['name','hit']].loc[df1['name'] == i].reset_index(drop=True)
                if df4['hit'][0].split('_')[0] == 'P':
                    cc.append(0.5)    
                elif df4['hit'][0].split('_')[0] == 'N':
                    cc.append(-0.5)  
            else:
                cc.append(0)
    else:
        cc = [0] * len(results_df1)

    df6 = pd.DataFrame()
    df6["ID"] = results_df1["ID"]
    df6['BLAST_Score'] = cc
    df6['ML_Score'] = results_df1["ML_Score"]
    df6['Total_Score'] = df6['ML_Score'] + df6['BLAST_Score']

    return df6





def run_option_2(input_file, output_file="output_results.csv"):
    save_fasta_sequences(input_file)  # Save FASTA sequences first

    folder_name = "file_split"
    feq_seq_path = "Fea_Seq"  # Path to the directory where you want to create the folder
    folder_path = os.path.join(feq_seq_path, folder_name)

    try:
        os.makedirs(folder_path)
    except FileExistsError:
        # If the folder already exists, remove it and create a new one
        try:
            shutil.rmtree(folder_path)  # Remove existing folder
            os.makedirs(folder_path)  # Create new folder
        except Exception as e:
            print("Error creating folder:", e)

    # PSSM feature extraction
    file_split("Fea_Seq/sequences.fasta", "Fea_Seq/file_split")
    # pssm profile generate 
    generate_pssm(folder_path)
    
    fasta_file = 'Fea_Seq/sequences.fasta'
    folder_path = 'Fea_Seq/file_split/pssm_raw'
    pssm_output_file = 'Fea_Seq/pssm_sequences.fasta'
    not_in_pssm_output_file = 'Fea_Seq/other.fasta'
    
    save_sequences_in_output_files(fasta_file, folder_path, pssm_output_file, not_in_pssm_output_file)

    # Check if not_in_pssm_output_file is empty
    if os.path.getsize(not_in_pssm_output_file) == 0:
        print("No sequences found in 'not_in_pssm_output_file'. Skipping option 1.")
    else:
        # Run option 1
        y_pred_proba_aac = run_option_1(not_in_pssm_output_file)

    subprocess.run(["python3", "PSSM/possum.py", "-i", "Fea_Seq/pssm_sequences.fasta", "-o", "Fea_Seq/PSSM_feature.csv", "-t", "pssm_composition", "-p", "Fea_Seq/file_split/pssm_raw"])
    subprocess.run(["python3", "PSSM/headerHandler.py", "-i", "Fea_Seq/PSSM_feature.csv", "-o", "Fea_Seq/Pssm_w_Header.csv", "-p", "PRR"])

    # Load the Extra Trees Classifier model with PSSM
    loaded_model2 = joblib.load("Models/ET_model.pkl")
    feature = pd.read_csv("Fea_Seq/Pssm_w_Header.csv")
    # Use the loaded model to make predictions on the test dataset
    y_pred_proba_pssm = loaded_model2.predict_proba(feature)[:, 1]

    # Read sequences from not_in_pssm_output_file
    with open(not_in_pssm_output_file, 'r') as f:
        not_in_pssm_sequences = [line.strip()[1:] for line in f.readlines() if line.startswith(">")]

    # Read the sequence IDs from the pssm_output_file
    with open(pssm_output_file, "r") as fasta_file:
        fasta_lines = fasta_file.readlines()
    headers_pssm = [line.strip()[1:] for line in fasta_lines if line.startswith(">")]

    # Combine results from both models
    if os.path.getsize(not_in_pssm_output_file) == 0:
        all_headers = headers_pssm
        all_probabilities = list(y_pred_proba_pssm)
    else:
        all_headers = not_in_pssm_sequences + headers_pssm
        all_probabilities = list(y_pred_proba_aac) + list(y_pred_proba_pssm)

    # Create a DataFrame with sequence IDs and probabilities
    results_df = pd.DataFrame({"ID": all_headers, "ML_Score": all_probabilities})
    # Drop duplicates
    results_df = results_df.drop_duplicates()
   
    # Save the DataFrame to a CSV file
    results_df.to_csv(output_file, mode='a', index=False, header=False)  # Append to existing file

    # Reload the CSV file to remove duplicates
    results_df = pd.read_csv(output_file)

    # Remove duplicates
    results_df1 = results_df.drop_duplicates()
    if os.path.exists("res.out"):
        os.remove("res.out")

    # Run blastp command
    subprocess.run(["blastp", "-task", "blastp", "-db", "Database/train", "-query", input_file , "-out", "res.out", "-outfmt", "6", "-evalue", "0.01"])
    # Process blast results
    blast_result_file = "res.out"
    df6 = process_blast_results(blast_result_file, results_df1)
    
    # Save the DataFrame to a CSV file
    df6.to_csv(output_file, index=False)
    print(f"Output of ET with PSSM saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Plant Disease Resistance Protein Prediction Tool")
    parser.add_argument("-i", "--input", help="Input FASTA file (.fasta format)")
    parser.add_argument("-o", "--output", help="Output CSV file name (default: output_results.csv)", default="output_results.csv")
    parser.add_argument("-m", "--model", help="Choose model option (1: AAC feature extraction and SVC model, 2: PSSM feature extraction and ET model)")
    
    args = parser.parse_args()

    if args.input and args.output and args.model:
        input_file = args.input
        output_file = args.output
        model_option = args.model

        if model_option == "1":
            run_option_1(input_file, output_file)
        elif model_option == "2":
            run_option_2(input_file, output_file)
        else:
            print("Invalid model option. Please choose either 1 or 2.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()




