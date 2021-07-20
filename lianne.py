

#####################################
# NAME: lianne.py
# AUTHOR: Luciano Giaco'
# Date: 06/07/2021
version = "0.1"
# ===================================


import os
import argparse
from shutil import copyfile

# GLOBAL PATH
RESULTS = '/data/novaseq/Diagnostic/NovaSeq/Results/'
TMP = '/data/novaseq/tmp'
DRAGEN = '/apps/trusight/2.2.0'
D_RESOUCES = '/apps/trusight/2.2.0/resources'


#####################################
# Classes
# ===================================

class pbs_parameters:

    def __init__(self, pathStd, select, ncpus, mem, email, sendMode, name, queue):

        # ARGUMENTS
        # 
        # pathStd = Folder path where stdin and stderr files will be created - String
        # select = Numebr of chunks request for PBS - Integer
        # ncpus = Number of cpus request for PBS - Integer
        # mem = Amount of RAM request for PBS in Gb - Integer
        # email = email adress used by PBS to send the email - String
        # sendMode = Send parameter mode 'abe' - String
        # name = Job name - String
        # queue = Queue to use on cluster - workq or gpuq 

        self.pathStdout = os.path.join(pathStd, 'stdout')
        self.pathStderr = os.path.join(pathStd, 'stderr')
        self.resources = 'select='+str(select)+':ncpus='+str(ncpus)+':mem='+str(mem)
        self.email = email
        self.sendMode = sendMode
        self.name = name
        self.queue = queue

    def getStdout(self):
        return self.pathStdout

    def getStderr(self):
        return self.pathStderr    

    def getResources(self):
        return self.resources

    def getEmail(self):
        return self.email

    def getMode(self):
        return self.sendMode

    def getName(self):
        return self.name

    def getQueue(self):
        return self.queue
            

#####################################
# Functions
# ===================================

def get_folderOut(runInput):
	head, tail = os.path.split(runInput)
	return(tail)

def build_param_sh(parameters):

	o = parameters.getStdout()
	e = parameters.getStderr()
	l = parameters.getResources()
	M = parameters.getEmail()
	m = parameters.getMode()
	N = parameters.getName()
	q = parameters.getQueue()

	
	par = '#! /bin/bash \n\n'
	par = par+'#PBS -o '+o+'\n'
	par = par+'#PBS -e '+e+'\n'
	par = par+'#PBS -l '+l+'\n'
	par = par+'#PBS -M '+M+'\n'
	par = par+'#PBS -m '+m+'\n'
	par = par+'#PBS -N '+N+'\n'
	par = par+'#PBS -q '+q+'\n\n'

	return(par)

def demultiplex_cl(runInput, tmp_fastq, samplesheet):
	# demultiplex command line
	
	d_cl = 'module load anaconda/3m\n'
	d_cl = d_cl+'conda init bash\n'
	d_cl = d_cl+'conda activate /data/hpc-data/shared/condaEnv/baseinstall/\n\n'
	d_cl = d_cl+'bcl-convert '
	d_cl = d_cl+'--bcl-input-directory '
	d_cl = d_cl+runInput+' '
	d_cl = d_cl+'--output-directory '
	d_cl = d_cl+tmp_fastq+' '
	d_cl = d_cl+'--sample-sheet '
	d_cl = d_cl+samplesheet

	return d_cl

def samplesheet_mamage(samplesheet):
	if os.path.isfile(samplesheet):
		return [True]
	else:
		# run folder list
		dirlist = os.listdir(runInput)
		# extract csv files
		matching = [s for s in dirlist if ".csv" in s]
		# control if there are more then one csv file
		# if not, copy the csv found with SampleSheet.csv name
		if len(matching) != 1:
			print('# WARNING - More than one csv file found\n# INFO exit')
			os.sys.exit()
		else:
			src = os.path.join(runInput, matching[0])
			copyfile(src, samplesheet)
		return [False, src]

def dragen_cl(out_dragen, runInput, samplesheet):
	dr_cl = 'module load singularity/3.7.4\n'
	dr_cl = dr_cl+'module load openmpi/4.1.1\n'
	dr_cl = dr_cl+'cd '+DRAGEN+'\n\n'
	dr_cl = dr_cl+'./TruSight_Oncology_500_RUO.sh '
	dr_cl = dr_cl+'--analysisFolder '
	dr_cl = dr_cl+out_dragen+' '
	dr_cl = dr_cl+'--resourcesFolder '
	dr_cl = dr_cl+D_RESOUCES+' '
	dr_cl = dr_cl+'--runFolder '
	dr_cl = dr_cl+runInput+' '
	dr_cl = dr_cl+'--engine singularity '
	dr_cl = dr_cl+'--sampleSheet '
	dr_cl = dr_cl+samplesheet+' '
	dr_cl = dr_cl+'--isNovaSeq'

	return(dr_cl)

####################
##  --> MAIN <--  ##
####################

def main(runInput, select, ncpus, mem, email, sendMode, name, queue):
	tail = get_folderOut(runInput)

	################
	# DEMULTIPLEXING

	# path management
	tmp_path = os.path.join(TMP, tail)
	tmp_path = os.path.normpath(tmp_path)
	#os.mkdir(tmp_path, mode = 0o755)

	tmp_fastq = os.path.join(tmp_path, 'fastq')
	#os.mkdir(tmp_fastq, mode = 0o755)

	d_file = os.path.join(tmp_path, 'demultiplex.sh')

	# sample sheet check
	samplesheet = os.path.join(runInput, 'SampleSheet.csv')
	control = samplesheet_mamage(samplesheet)
	print(control)
	if control[0] == False:
		print('# INFO - Found a SampleSheet with different name\n# INFO - '+control[1]+' copied as SampleSheet.csv')


	# pbs parameters
	parameters = pbs_parameters(tmp_path, select, ncpus, mem, email, sendMode, name, queue)
	par = build_param_sh(parameters)

	# command line
	d_cl = demultiplex_cl(runInput, tmp_fastq, samplesheet)
	d_sh = par+d_cl

################################
### DECOMMENTA
	# build sh file
	# sh = open(d_file, 'w')
	# sh.write(d_sh)
	# sh.close()

	# send job
	# os.system('qsub '+d_file)

	################
	# DRAGEN

	# path management
	
	out_dragen = os.path.join(RESULTS, tail)
	pathStd = pbs_parameters(out_dragen, select, ncpus, mem, email, sendMode, name, queue)
	par = build_param_sh(pathStd)

	dr_file = os.path.join(tmp_path, 'dragen.sh')

	dr_cl = dragen_cl(out_dragen, runInput, samplesheet)
	dr_sh = par+dr_cl
	print(dr_sh)
	os.sys.exit()

	# build sh file
	sh = open(dr_file, 'w')
	sh.write(dr_sh)
	sh.close()

	# send job
	os.system('qsub '+dr_file)




if __name__ == '__main__':
	# parser variable
	parser = argparse.ArgumentParser(description='Lims Management System - Lianne')

	# arguments
	parser.add_argument('-i', '--runInput', required=True,
						help='NovaSeq output sequencing path')
	parser.add_argument('-l_select', '--select', required=False,
						default = 1,
						help='Select the number of chunks to send on PBS cluser - Default=1')
	parser.add_argument('-l_ncpus', '--ncpus', required=False,
						default = 24,
						help='Select the number of ncpus to require - Default=24')
	parser.add_argument('-l_mem', '--mem', required=False,
						default = 128,
						help='Select the amount of memory to require - Default=128')
	parser.add_argument('-e', '--email', required=False,
						default = 'luciano.giaco@policlinicogemelli.it',
						help='Insert the email - Default=luciano.giaco@policlinicogemelli.it')
	parser.add_argument('-m', '--sendMode', required=False,
						default = 'ae',
						help='Insert the sending email mode - Default=ae')
	parser.add_argument('-N', '--name', required=False,
						default = 'lianne',
						help='Insert the job name - Default=lianne')
	parser.add_argument('-q', '--queue', required=False,
						default = 'workq',
						help='Insert the queue to send job - Default=workq')
	


	args = parser.parse_args()
	runInput = args.runInput
	select = args.select
	ncpus = args.ncpus
	mem = args.mem
	email = args.email
	sendMode = args.sendMode
	name = args.name
	queue = args.queue

	main(runInput, select, ncpus, mem, email, sendMode, name, queue)