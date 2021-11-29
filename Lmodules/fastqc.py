

#####################################
# NAME: fastqc.py
# AUTHOR: Luciano Giaco'
# Date: 29/11/2021
version = "0.1"
# ===================================

# Part of Lianne system

import os
import argparse
import subprocess


par = ("#! /bin/bash \
\n \
#PBS -o /data/novaseq_results/tmp/analysis_211122_A01423_0012_AH2YWCDRXY/stdout_FastQC \n\
#PBS -e /data/novaseq_results/tmp/analysis_211122_A01423_0012_AH2YWCDRXY/stderr_FastQC \n\
#PBS -l select=1:ncpus=10:mem=20g \n\
#PBS -M luciano.giaco@policlinicogemelli.it \n\
#PBS -m ae \n\
#PBS -N lianne_FastQC \n\
#PBS -q workq")

def main(fastq_folder, tmp_path, jobid2_str):
	
	dr_cl = 'module load anaconda/3\n'
	dr_cl = dr_cl+'init bash\n'
	dr_cl = dr_cl+'source ~/.bashrc\n'
	dr_cl = dr_cl+'conda activate /data/hpc-data/shared/pipelines/varan/varan_env\n'
	dr_cl = dr_cl+'\n'
	dr_cl = dr_cl+'\n'

	# append all FastQC call
	# in the Illumina fastq local app output folder 
	for root, dirs, files in os.walk(fastq_folder, topdown=False):
		for name in files:
			if '.fastq.gz' in name:
				fastq = os.path.join(root, name)
				out, file = os.path.split(fastq)
				if 'Undetermined' in out:
					continue
				dr_cl = dr_cl+('fastqc '+fastq+' -o '+out+'\n\n')

	dr_sh = par+dr_cl


	# build fastqc job
	FastQC_file = os.path.join(tmp_path, 'FastQC.sh')

	# build sh file
	sh = open(FastQC_file, 'w')
	sh.write(dr_sh)
	sh.close()
	if jobid2_str is None:
		subprocess.run(['qsub', FastQC_file], stdout=subprocess.PIPE, universal_newlines=True)
	else:
		dependencyID = 'depend=afterany:'+jobid2_str
		jobid2 = subprocess.run(['qsub', '-W', dependencyID, FastQC_file], stdout=subprocess.PIPE, universal_newlines=True)

if __name__ == '__main__':
	
	parser = argparse.ArgumentParser(description='FastQC')

	# arguments
	parser.add_argument('-f', '--FastqFolder', required=True,
							help='Fastq folder of Illumina app [eg. path/Logs_Intermediates/FastqGeneration]')
	parser.add_argument('-t', '--tmp_path', required=True,
							help='Folder where sh file will be write')
	parser.add_argument('-j', '--jobid2_str', required=False,
							help='PBS jobID to wait if the script is submitted in queue')

	args = parser.parse_args()
	fastq_folder = args.FastqFolder
	tmp_path = args.tmp_path
	jobid2_str = args.jobid2_str

	main(fastq_folder, tmp_path, jobid2_str)



