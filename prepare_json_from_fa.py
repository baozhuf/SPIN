import json, os, argparse
from datetime import datetime as dt

def get_args():
    parser = argparse.ArgumentParser("Pipeline to prepare json files for AlphaFold3")

    parser.add_argument( "--fa1_path", type=str, help="Absolute path for the fasta file 1 to be used to prepare json files for AF3")
    parser.add_argument( "--fa2_path", type=str, default=None, help="Absolute path for the fasta file 1 to be used to prepare json files for AF3")
    parser.add_argument( "--len_cutoff", type=int, default=1000, choices=range(1, 10000), help="threshold to separate sequences as long or short", long sequences need more Memory)
    parser.add_argument( "--protein1_cnt", type=int, default=1, choices=range(1, 200), help="number of copies for a protein from fa1")
    parser.add_argument( "--protein2_cnt", type=int, default=1, choices=range(1, 200), help="number of copies for a protein from fa2")
    parser.add_argument( "--num", type=int, default=30, choices=range(1, 1000000), help="number of protein-protein pairs in a json file")
    parser.add_argument( "--today", type=str, default="20250501" , help="use the same dateTime as previous processes to name dir and joson files")
    parser.add_argument( "--out_dir", type=str, default="./" , help="the output directory for the prepared json files")

    args = parser.parse_args()
    return args

def fa_to_dict(fa_path, length_cutoff=1000):
    
    """
    convert a fasta file into two python dictionaries, the first dict has shorter protein length
    the second dict has longer protein length, based on the length_cutoff
    input: fasta file path, optional cutoff value
    output: two dictionaries and a string: one with shorter seqs, one with longer seqs; the stem string used for saving json files in the next function.
    """
    
    ########### step 0 preparation
    # initialize some storages
    file_items = [] # empty list to store all items read from a fasta file, for easy checking the end of the file
    seqNMs = [] # empty list to store sequence headers
    seqs = [] # empty list to store sequences
    seq = "" # empty string to concatinate all lines of a sequence
    
    # open fasta file
    with open(fa_path, "r") as file:
        for line in file:
            line = line.strip() # remove the "\n" empty line
            file_items.append(line) # collect all none-empty lines 

    for i in range(len(file_items)): # using index to easily check the end of the list
        
        # if the line starts with ">", this line is a header
        if file_items[i][:1] == ">":
            # store the sequence name/header
            seqNMs.append(file_items[i][1:].split(" ")[0].split("|")[0]) # remove ">" and " " or "|" for the case of alphafoldserver.com
            
            # store the previous sequence
            if seq: # avoid saving the empty string when i=0 at the first header
                seqs.append(seq)
                
            # initialize seq
            seq = ""
            
        # if the line does not start with ">", this line is a sequence line
        else:
            seq = seq + file_items[i] # convert multi-line sequence to one-line
            
        # if i reached the end, append the last seq, which couldn't be appended during the first if statement
        if i == len(file_items) -1 :
            seqs.append(seq) 
    
    ############ step 1 convert two lists to a dictionary
    dic = dict(zip(seqNMs, seqs))
    
    ############ step 2 separate dic to two dicts baased on length_cutoff
    dic_short = {}
    dic_long = {}
    
    for key, val in dic.items():
        if len(val) < length_cutoff:
            dic_short[key] = val
        else:
            dic_long[key] = val
            
    ############# step 3 get the stems of fasta file names for naming json files
    fa_stem = fa_path.split("/")[-1].rsplit(".", 1)[0] # rsplit(separator, maxsplit). maxsplit=1, will return a list with 2 elements!
    
    return dic_short, dic_long, fa_stem
    
    

def prep_save_json_keystep(proteins1, fa1_stem, proteins2=None, fa2_stem="", protein1_count=1, protein2_count=1, n=30, today="20250501", out_dir="./"):
    """
    prepare json files that contains pairs of 2 proteins for AF3 on both alphafoldserver.com and HiPerGator
    input: 1) one proteins dictionary for all possible combinations of 2-pair proteins
           2) or two proteins dictionaies for all vs all pairing of 2 proteins
           3) n is the number of pairs in a json file, it is recommended as 30 for alphafoldserver.com, < 300 for HiPerGator due to the GPU time limitation (14 days)
    output: json files. Each json file has at most n 2-proteins pairs.
    """
     
    proteins1_keys = list(proteins1.keys()) # list() convert dict_keys obj to List obj
    
    # helpers
    data = [] # empty list to store final results
    counter = 0 # determine when to save a json file
    # today = dt.now().strftime("%Y%m%d_%H%M%S") # use dateTime to name dir and joson files

    for i in range(len(proteins1)):

        # determin the start, end, prt2, and prt2_keys based on the availability of proteins2
        if proteins2:
            start = 0
            end = len(proteins2)
            prt2 = proteins2
            prt2_keys = list(proteins2.keys()) # list() convert dict_keys obj to List obj
        else:
            start = i
            end = len(proteins1)
            prt2 = proteins1
            prt2_keys = proteins1_keys

        # 3 updates
        for j in range(start, end):

            counter += 1

            # create a template dictionary to store protein-protein pair
            temp = {'name': 'protein1_protein2',
                    'modelSeeds': [2025],
                    'sequences': [{'proteinChain': {'sequence': 'ATCG', 'count': protein1_count}},
                                  {'proteinChain': {'sequence': 'ATCG', 'count': protein2_count}},
                                 ]
                   }

            # update job name
            temp["name"]= proteins1_keys[i] + "--VS--" + prt2_keys[j]

            # update the first protein
            temp["sequences"][0]['proteinChain']['sequence'] = proteins1[proteins1_keys[i]]

            # update the second protein
            temp["sequences"][1]['proteinChain']['sequence'] = prt2[prt2_keys[j]]

            # add to the final list
            data.append(temp)

            # Going to save json file with all items been updated
            # create a folder if not exist
            new_dir = os.path.join(out_dir, f"{today}_af3_jsons")
            os.makedirs(new_dir, exist_ok=True)

            # if the data list stored n items, save as a json file
            if len(data) == n:
                path = f"{new_dir}/{today}_{fa1_stem}_{fa2_stem}_{protein1_count}+{protein2_count}mer-{counter//n}.json"
                with open(path, "w") as jsonFile:
                    json.dump(data, jsonFile)
                data = [] # reset the result list!

            # elif i and j reached the ends
            elif (i == len(proteins1) - 1) and (j == end - 1):
                if data:
                    path = f"{new_dir}/{today}_{fa1_stem}_{fa2_stem}_{protein1_count}+{protein2_count}mer-{counter//n + 1}.json"
                    with open(path, "w") as jsonFile:
                        json.dump(data, jsonFile)
                        
                        

# Prepare json files for AlphaFold3
def prep_json_multimer(fa1_path, fa2_path=None, length_cutoff=1000, protein1_count=1, protein2_count=1, n=30, today="20250501", out_dir="./"):
    """
    prepare json files that contains pairs of 2 proteins for AF3 on both alphafoldserver.com and HiPerGator
    input: 1) one fasta file for all possible combinations of 2-pair proteins
           2) or two fasta files for all vs all pairing of 2 proteins
           3) n is the number of pairs in a json file, it is recommended as 30 for alphafoldserver.com, < 300 for HiPerGator due to the GPU time limitation (14 days)
    output: json files. Each json file has at most n 2-proteins pairs.
    """
    # get the protein dictionaries and path_stems for the two fa files
    fa1s = fa_to_dict(fa1_path, length_cutoff) # fa1s is a tuple of (prot1_short, prot1_long, fa1_stem)
    if fa2_path:
        fa2s = fa_to_dict(fa2_path, length_cutoff) # fa2s is a tuple of (prot2_short, prot2_long, fa2_stem)
    
    for i in range(2): # using index, not protein_short/long, for labeling fa_stems: 0-0 short-short, 0-1 short-long, 1-0 long-short, 1-1 long-long
        for j in range(2):
            prep_save_json_keystep(proteins1=fa1s[i],
                                   fa1_stem=fa1s[2] + "_" + str(i), # to label long-short (1-0)
                                   proteins2=fa2s[j],
                                   fa2_stem=fa2s[2] + "_" + str(j), # to label long-short (1-0)
                                   protein1_count=protein1_count, 
                                   protein2_count=protein1_count, 
                                   n=n, 
                                   today=today, 
                                   out_dir=out_dir
                                   )


# 3 prepare json files
# get the options
opts = get_args()
fa1_path=opts.fa1_path
fa2_path=opts.fa2_path
len_cutoff=opts.len_cutoff
protein1_count=opts.protein1_cnt
protein2_count=opts.protein2_cnt
n=opts.num
today=opts.today
out_dir=opts.out_dir

prep_json_multimer(fa1_path, fa2_path, len_cutoff, protein1_count, protein2_count, n, today, out_dir)
