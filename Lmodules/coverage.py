###############################################
# NAME : coverage.py
# AUTHOR: Luciano Giaco'
# Date: 20-10-2021
# =============================================
#
# DESCRIPTION
# ----------------
# Quality control script. It gets the bam file and it 
# check for coverage at different reads depths. It returns a xlsx and txt file
# 
# USAGE
# --------------
# See usage() function or use the -h option
#    
# Version
# --------------
version = "1.1"
###############################################

import openpyxl as px
from openpyxl.styles import PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.formatting.rule import CellIsRule

import os 
import argparse
import subprocess


BED='/data/hpc-data/shared/pipelines/lianne/conf/TST500C_manifest.bed'


def checkFile(inFile):
	if os.path.isfile(inFile):
		root, tail = os.path.split(inFile)
		prefix, extension = os.path.splitext(tail)
		return prefix
	else:
		print('ERROR: '+inFile)
		print('ERROR: is not a file')
		os.sys.exit()


def mosdepth_cl(bedFile, threshold, prefix, inBam):
	m_cl = 'mosdepth '
	m_cl = m_cl+'--by '
	m_cl = m_cl+bedFile+' '
	m_cl = m_cl+'--threshold '
	m_cl = m_cl+threshold+' '
	m_cl = m_cl+prefix+' '
	m_cl = m_cl+inBam

	return m_cl

def manage_out_dir(ot, prefix):
	
	# ot: snv or cnv or rna

	# coverage dir
	if ot == 'snv':
		prx = 'snv_'
	elif ot == 'rna':
		prx = 'rna_'
	elif ot == 'cnv':
		prx = 'cnv_'
	else:
		print('[ERROR] Prefix coverage folder out not defined')
		print('[INFO] Exit')
		os.sys.exit()

	cwd = os.getcwd()
	out_dir = os.path.join(cwd, prx+'coverage')

	# making dir and move inside
	try:
		print('[INFO] Making '+out_dir)
		os.mkdir(out_dir, mode = 0o755)
		print('[INFO] Directory '+out_dir+' created')
		print('[INFO] Moving '+out_dir)
		os.chdir(out_dir)
	except FileExistsError:
		print('[INFO] Directory '+out_dir+' already exists')
		print('[INFO] Moving '+out_dir)
		os.chdir(out_dir)

	# sample dir
	sample_dir = os.path.join(out_dir, prefix)

	try:
		print('[INFO] Making '+sample_dir)
		os.mkdir(sample_dir, mode = 0o755)
		print('[INFO] Directory '+sample_dir+' created')
		print('[INFO] Moving '+sample_dir)
		os.chdir(sample_dir)
	except FileExistsError:
		print('[INFO] Directory '+sample_dir+' already exists')
		print('[INFO] Moving '+sample_dir)
		os.chdir(sample_dir)

def main(inBam, threshold, bedFile, ot):

	################### CONTROL FILES
	
	### Bam file
	prefix = checkFile(inBam)
	### Bed file
	if bedFile != BED:
		checkFile(bedFile)

	################ MANAGE DIRECTORY

	manage_out_dir(ot, prefix)


	############## BUILD COMMAND LINE

	m_cl = mosdepth_cl(bedFile, threshold, prefix, inBam)
	submitted = m_cl.split()
	subprocess.run(submitted)
	print(m_cl)




if __name__ == '__main__':
	# parse arguments
	parser = argparse.ArgumentParser(description='Quality control script. It gets the bam file and it \n\
check for coverage at different reads depths. It returns a xlsx and txt file')

###########################################################################

	parser.add_argument('-i', '--inBam', required=True,
						help='Absolute path file of bam')
	parser.add_argument('-t', '--threshold', required=False,
						default='5,10,50,100,250,500',
						help="for each interval in bed file, write number of bases covered by at\
least threshold bases. Specify multiple integer values separated\
by ','")
	parser.add_argument('-b', '--bedFile', required=False,
						default=BED)
	parser.add_argument('-p', '--output_prefix', required=True,
						help="Prefix of output folder.\nSelections allowed: snv, rna, cnv",
						choices=['snv', 'rna', 'cnv'])

###########################################################################


	args = parser.parse_args()
	inBam = args.inBam
	threshold = args.threshold
	bedFile = args.bedFile
	ot = args.output_prefix


###########################################################################

	main(inBam, threshold, bedFile, ot)

