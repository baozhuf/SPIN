# Project Overview

SPIN: A Scalable Bioinformatics Pipeline for Screening Pathogenicity-Related Host-Pathogen Protein INteractions Using AlphaFold3

SPIN provides a unified framework for protein structure prediction and interaction analysis using both institutional HPC (UF HiPerGator) and cloud-based AlphaFold workflows. It automates data preparation, JSON generation, and post-analysis for large scale protein-protein interaction screening.

# 🔄 Workflow Diagram

<img width="3242" height="730" alt="image" src="https://github.com/user-attachments/assets/c6f3c978-a1dd-4fa9-9f0e-7099762c396c" />

**Pipeline Stages**

SignalP: Predicts secreted proteins from pathogen sequences.  
OrthoFinder: Identifies orthologous groups.  
CD-HIT: Clusters proteins to reduce redundancy.  
JSON Preparation: Generates input files for AlphaFold3.  
AlphaFold3: Predicts protein-protein interactions.  
Post-Analysis: Extracts and ranks interaction confidence scores.  


---
# Key Features
- predict secreted proteins from pathogen
- Remove redundancy before AlphaFold 3 screening
- Automated JSON preparation for AlphaFold server integration
- Post-analysis tools for metrics extraction

---

## 📁 Repository Contents

- `spin.sh`: A full pipeline script that integrates SignalP, OrthoFinder, CD-HIT, AlphaFold3, and post-analysis into a Slurm job.
- `prepare_json_from_fa.py`: Prepares JSON files from FASTA sequences for AlphaFold3 multimer predictions.
- `post_analysis.py`: Summarizes AlphaFold3 output generated from HiPerGator by extracting and ranking confidence scores.
- `post_analysis_AF3server.py`: Summarizes AlphaFold3 output generated from alphafoldserver.com by extracting and ranking confidence scores.

---

# ⚙️ Prerequisites

- Python 3.x
- Slurm Workload Manager
- Singularity
- Required tools:
  - SignalP 6.0
  - OrthoFinder
  - CD-HIT
  - AlphaFold3
- pandas


# 🚀 Installation
Clone the repository:

git clone https://github.com/baozhuf/spin.git

cd spin

# 🧪 Usage
<img width="1622" height="499" alt="image" src="https://github.com/user-attachments/assets/d1514c16-4c61-4bf9-8a25-465498447fc3" />

## Scenario 1. Run the Full Pipeline with Slurm on UF HiPerGator computing platform
bash spin.sh \
  -a your_slurm_account \
  -e your_email@ufl.edu \
  -p ./pathogen_fasta_dir \
  -i ./host_fasta_dir \
  -l /path/to/af3_model_parameters \
  -f 0.5 \
  -o ./AF3_out

## Scenario 2. You only want to Prepare JSONs for AlphaFold3 on alphafoldserver.com
python prepare_json_from_fa.py \
  --fa1_path path/to/pathogen.fa \
  --fa2_path path/to/host.fa \
  --protein1_cnt 1 \
  --protein2_cnt 1 \
  --num 30 \
  --today 20250501 \
  --out_dir ./output_jsons

## Scenario 3. You only want to Run Post-Analysis to extract AlphaFold3 metrics (pTM, ipTM, ipSAE, pDockQ)

**AlphaFold3 outputs obtained from UF HiPerGator**

python post_analysis.py \
  --af3_out_dir ./AF3_out \
  --summary_path ./AF3_out/af3_results_summary.csv

**AlphaFold3 outputs obtained from alphafoldserver.com**

python post_analysis_AF3server.py \
  --af3_zf_dir ./AF3_out \
  --summary_path ./AF3_out/af3_results_summary.csv


# 🧾 Script Argument Descriptions (spin.sh)
| Flag | Description |
|------|-------------|
| `-a` | Slurm account name (required) |
| `-e` | Email for job notifications (required) |
| `-c` | Number of CPUs (default: 4) |
| `-m` | Memory in GB (default: 62) |
| `-d` | Number of days for job runtime (default: 1) |
| `-p` | Pathogen FASTA directory (required) |
| `-i` | Host FASTA directory (required) |
| `-l` | AlphaFold3 model parameter directory (required) |
| `-f` | CD-HIT cutoff (range: 0.4–1.0, default: 0.5) |
| `-o` | Output directory (default: `./AF3_out`) |


# Reference

bioRxiv 2026.04.21.719732; doi: https://doi.org/10.64898/2026.04.21.719732

# 📬Contact
For questions or collaboration inquiries, please contact:
Zhenghong Bao
📧 z.bao@ufl.edu


# 📄 License
This project is licensed under the MIT License.

