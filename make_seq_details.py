

#####################################
# NAME: make_seq_details.py
# AUTHOR: Luciano Giaco'
# Date: 24/08/2021
version = "0.1"
# ===================================


import os
import csv
import sys
import re

HEADER = 'ACCESSION NUMBER,SPECIMEN LABEL,RUN ID,LANE,BARCODE,SEQUENCING TYPE,SAMPLE TYPE,SAMPLE Id'

def read_csv(samplesheet_file):
	samplesheet = open(samplesheet_file, newline='')
	ss_reader = csv.reader(samplesheet, delimiter=',')
	return ss_reader

def get_runID(samplesheet_file):
	root, file = os.path.split(samplesheet_file)
	root, run_ID = os.path.split(root)
	return run_ID

def get_dict_data(ss_reader):
	flag = False
	data_dict = dict()
	for row in ss_reader:
		if row[0] == '[Data]':
			flag = True
			continue
		if flag:
			# d_row = (','.join(row))
			data_dict[row[0]]=row
	return data_dict

def get_details(data_dict, run_ID):
	# accession_number is patient
	# 
	details_dict = dict()
	for k,v in data_dict.items():
		row_to_write = []
		if k == 'Sample_ID':
			continue
		sample_ID = k
		idx1 = v[5]
		idx2 = v[6]
		sample_Type = v[7]
		accession_number = v[8]
		row_to_write.append(accession_number)
		row_to_write.append('Primary Specimen')
		row_to_write.append(run_ID)
		row_to_write.append('1')
		row_to_write.append(idx1+'-'+idx2)
		row_to_write.append('PAIRED END')
		row_to_write.append(sample_Type)
		row_to_write.append(sample_ID)
		details_dict[sample_ID] = row_to_write
		#continue
	return details_dict
	

def main(samplesheet_file):
	print(samplesheet_file)
	#
	ss_reader = read_csv(samplesheet_file)
	run_ID = get_runID(samplesheet_file)
	data_dict = get_dict_data(ss_reader)
	details_dict = get_details(data_dict, run_ID)
	file_name = run_ID+'_Details.csv'
	file_out = open(file_name, 'w')
	print(file_name)
	file_out.write(HEADER+'\n')
	for k,v in details_dict.items():
		file_out.write(','.join(v))
		file_out.write('\n')
	file_out.close()




if __name__ == '__main__':
	samplesheet_file = sys.argv[1]
	main(samplesheet_file)

