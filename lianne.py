

#####################################
# NAME: lianne.py
# AUTHOR: Luciano Giaco'
# Date: 06/07/2021
version = "0.1"
# ===================================


import os
import argparse
import subprocess
import make_seq_details
from shutil import copyfile

# GLOBAL PATH
RESULTS = '/data/novaseq_results/'
TMP = '/data/novaseq_results/tmp'
LOCAL_APP = '/apps/trusight/2.2.0'
D_RESOUCES = '/apps/trusight/2.2.0/resources'
LIANNE_FOLDER = '/data/hpc-data/shared/pipelines/lianne/'
COV_MODULE = os.path.join(LIANNE_FOLDER, 'Lmodules/coverage.py')


#####################################
# Classes
# ===================================

class pbs_parameters:

    def __init__(self, pathStd, select, ncpus, mem, email, sendMode, name, queue, m):

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

        self.pathStdout = os.path.join(pathStd, 'stdout_'+m)
        self.pathStderr = os.path.join(pathStd, 'stderr_'+m)
        self.resources = 'select='+str(select)+':ncpus='+str(ncpus)+':mem='+str(mem)
        self.email = email
        self.sendMode = sendMode
        self.name = name+'_'+m
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
	pathInput = os.path.normpath(runInput)
	head, tail = os.path.split(pathInput)
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

def demultiplex_cl(tmp_fastq, runInput, samplesheet):
	# demultiplex command line
	
	d_cl = 'module load singularity/3.7.4\n'
	d_cl = d_cl+'module load openmpi/4.1.1\n'
	d_cl = d_cl+'cd '+LOCAL_APP+'\n\n'
	d_cl = d_cl+'./TruSight_Oncology_500_RUO.sh '
	d_cl = d_cl+'--analysisFolder '
	d_cl = d_cl+tmp_fastq+' '
	d_cl = d_cl+'--resourcesFolder '
	d_cl = d_cl+D_RESOUCES+' '
	d_cl = d_cl+'--runFolder '
	d_cl = d_cl+runInput+' '
	d_cl = d_cl+'--engine singularity '
	d_cl = d_cl+'--sampleSheet '
	d_cl = d_cl+samplesheet+' '
	d_cl = d_cl+'--isNovaSeq '
	d_cl = d_cl+'--demultiplexOnly'

	return d_cl

def samplesheet_manage(samplesheet, tmp_path, debug):
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
			samplesheet = os.path.join(tmp_path, 'SampleSheet.csv')
			if debug is False:
				copyfile(src, samplesheet)
		return [False, samplesheet]

def localApp_cl(out_localApp, runInput, samplesheet):
	dr_cl = 'module load singularity/3.7.4\n'
	dr_cl = dr_cl+'module load openmpi/4.1.1\n'
	dr_cl = dr_cl+'cd '+LOCAL_APP+'\n\n'
	dr_cl = dr_cl+'./TruSight_Oncology_500_RUO.sh '
	dr_cl = dr_cl+'--analysisFolder '
	dr_cl = dr_cl+out_localApp+' '
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

def main(runInput, select, ncpus, mem, email, sendMode, name, queue, debug):
	
	
	tail = get_folderOut(runInput)
	print('TAIL')
	print(tail)
	################
	# DEMULTIPLEXING

	# path management
	# analysis folder will created
	# eg. analysis_210729_A01423_0009_AH33WGDRXY
	tmp_path = os.path.join(TMP, 'analysis_'+tail)
	tmp_path = os.path.normpath(tmp_path)

	if debug is False:
		try:
			os.mkdir(tmp_path)
		except FileExistsError:
			print('[WARNING] directory '+tmp_path+' already exists')
			pass
	
	# path folder used in d_file as --analysisFolder parameter
	tmp_fastq = os.path.join(tmp_path, tail)
	if debug is True:
		print('[DEBUG] path folder used in d_file as --analysisFolder parameter')
		print(tmp_fastq)
		print('\n')
	

	# sample sheet check
	samplesheet = os.path.join(runInput, 'SampleSheet.csv')
	control = samplesheet_manage(samplesheet, tmp_path, debug)
	
	if control[0] == False:
		print('# INFO - Found a SampleSheet with different name\n# INFO - '+control[1]+' copied')
		samplesheet = control[1]
	
	
	
	

################################
### QSUB JOBS

	################
	# Demultiplexing

	# pbs parameters
	parameters = pbs_parameters(tmp_path, select, ncpus, mem, email, sendMode, name, queue, 'demultiplex')
	par = build_param_sh(parameters)

	# command line
	d_cl = demultiplex_cl(tmp_fastq, runInput, samplesheet)
	d_sh = par+d_cl

	## DEBUG
	if debug is True:
		print('[DEBUG] Demultiplexing PBS parameters')
		print(par)
		print('\n')

	# build sh file
	d_file = os.path.join(tmp_path, 'demultiplex.sh')

	## DEBUG
	if debug is False:
		sh = open(d_file, 'w')
		sh.write(d_sh)
		sh.close()
	
		# Demultiplexing job
		print('[INFO] Sending '+d_file)
	
		# Capture the job ID for qsub hold
		jobid1 = subprocess.run(['qsub', d_file], stdout=subprocess.PIPE, universal_newlines=True)
		jobid1_str = jobid1.stdout
		print('[INFO] Queue:')
		subprocess.run(['qstat'])
	else:
		print('[DEBUG] sh file written in foder: ')
		print(d_file)
		print('[DEBUG] sh file contains: ')
		print(d_sh)
		print('\n\n\n')

	
	
	################
	# localApp

	# path management
	
	out_localApp = os.path.join(RESULTS, tail)
	select = 2
	pathStd = pbs_parameters(out_localApp, select, ncpus, mem, email, sendMode, name, queue, 'LocalApp')
	par = build_param_sh(pathStd)

	## DEBUG
	if debug is True:
		print('[DEBUG] Local App PBS parameters')
		print(par)
		print('\n')

	# path local app sh file
	dr_file = os.path.join(tmp_path, 'localApp.sh')

	# local app command line
	dr_cl = localApp_cl(out_localApp, runInput, samplesheet)

	# sh file to send
	dr_sh = par+dr_cl

	if debug is False:
		# build sh file
		sh = open(dr_file, 'w')
		sh.write(dr_sh)
		sh.close()

		# send job
		jobid2 = subprocess.run(['qsub', dr_file], stdout=subprocess.PIPE, universal_newlines=True)
		jobid2_str = jobid2.stdout
	else:
		print('[DEBUG] localApp file written in foder: ')
		print(dr_file)
		print('[DEBUG] localApp file contains:')
		print(dr_sh)
		print('[DEBUG] output folder of local app:')
		print(out_localApp)



	################
	# Upload to CGW
	

	# pbs parameters
	select = 1
	ncpus = 5
	mem = '80g'
	parameters = pbs_parameters(tmp_path, select, ncpus, mem, email, sendMode, name, queue, 'cgwUpload')
	par = build_param_sh(parameters)

	## DEBUG
	if debug is True:
		print('[DEBUG] CGWRunUploader PBS parameters')
		print(par)
		print('\n')


	dr_cl = 'module load corretto/8.292.10.1\n'
	dr_cl = dr_cl+'cd /data/hpc-share/illumina/test/pdx/CGWRunUploader\n'
	dr_cl = dr_cl+'\n'
	dr_cl = dr_cl+'java -jar '
	dr_cl = dr_cl+'-Dloader.main=com.pdx.commandLine.ApplicationCommandLine RunUploader-1.13.jar '
	dr_cl = dr_cl+'--commandLine '
	dr_cl = dr_cl+'--runFolder='+tmp_fastq+' '
	dr_cl = dr_cl+'--sequencer=Illumina '
	dr_cl = dr_cl+'--sequencerFileType=fastq'

	dr_sh = par+dr_cl
	# path management
	cgw_file = os.path.join(tmp_path, 'cgw_uploader.sh')

	if debug is False:
		# build sh file
		sh = open(cgw_file, 'w')
		sh.write(dr_sh)
		sh.close()
		dependencyID = 'depend=afterany:'+jobid1_str
		jobid2 = subprocess.run(['qsub', '-W', dependencyID, cgw_file], stdout=subprocess.PIPE, universal_newlines=True)
	else:
		print('[DEBUG] cgw_uploader.sh file written in foder: ')
		print(cgw_file)
		print('[DEBUG] cgw_uploader.sh file contains:')
		print(dr_sh)
		print('\n')
		

	###############
	# FastQC

	# pbs parameters
	select = 1
	ncpus = 10
	mem = '20g'
	parameters = pbs_parameters(tmp_path, select, ncpus, mem, email, sendMode, name, queue, 'FastQC')
	par = build_param_sh(parameters)

	dr_cl = 'module load anaconda/3\n'
	dr_cl = dr_cl+'init bash\n'
	dr_cl = dr_cl+'source ~/.bashrc\n'
	dr_cl = dr_cl+'conda activate /data/hpc-data/shared/condaEnv/lianne\n'
	dr_cl = dr_cl+'\n'
	dr_cl = dr_cl+'\n'
	
	# Set folder where Fastq are located
	# in the Illumina local app output folder
	# and append all FastQC call
	fastq_folder = os.path.join(tmp_fastq, 'Logs_Intermediates/FastqGeneration/*/*.fastq.gz')
	print(tmp_fastq)
	print(fastq_folder)
	
	fastqc_path = os.path.join(LIANNE_FOLDER, 'Lmodules/fastqc.py')
	sh_cmd = fastqc_path+' -f '+fastq_folder#+' -t '+tmp_path

	dr_sh = par+'\n\n'+dr_cl+sh_cmd
	FastQC_file_run = os.path.join(tmp_path, 'FastQC_run.sh')
	

	if debug is False:
		# build sh file
		sh = open(FastQC_file_run, 'w')
		sh.write(dr_sh)
		sh.close()
		dependencyID = 'depend=afterany:'+jobid2_str
		jobid3 = subprocess.run(['qsub', '-W', dependencyID, FastQC_file_run], stdout=subprocess.PIPE, universal_newlines=True)
	else:
		print('[DEBUG] FastQC.sh file written in foder: ')
		print(FastQC_file_run)
		print('[DEBUG] FastQC.sh file contains:')
		print(dr_sh)
		print(par)


	

	###############
	# Coverage

	# pbs parameters
	select = 1
	ncpus = 5
	mem = '10g'

	pathStd = pbs_parameters(out_localApp, select, ncpus, mem, email, sendMode, name, queue, 'coverage')
	par = build_param_sh(pathStd)

	dr_cl = 'module load anaconda/3\n'
	dr_cl = dr_cl+'init bash\n'
	dr_cl = dr_cl+'source ~/.bashrc\n'
	dr_cl = dr_cl+'conda activate /data/hpc-data/shared/condaEnv/lianne\n'
	dr_cl = dr_cl+'cd '+out_localApp
	dr_cl = dr_cl+'\n'
	dr_cl = dr_cl+'\n'

	dr_sh = par+'\n\n'+dr_cl

	
	
	# scrivere sh che lancia cvLaunch.py

	# write coverage sh
	# pbs parameters
	select = 1
	ncpus = 1
	mem = '1g'

	pathStd = pbs_parameters(out_localApp, select, ncpus, mem, email, sendMode, name, queue, 'coverage')
	par = build_param_sh(pathStd)
	cv_sh = par+'\n\n'
	cv_sh = cv_sh+'cd '+LIANNE_FOLDER+'\n'
	cv_sh = cv_sh+'python3 Lmodules/cvLaunch.py -p '+dr_sh+' -o '+out_localApp

	cvLaunch = os.path.join(out_localApp, 'cvLaunch.sh')


	if debug is False:
		sh = open(cvLaunch, 'w')
		sh.write(cv_sh)
		sh.close()
		dependencyID = 'depend=afterany:'+jobid2_str
		jobid4 = subprocess.run(['qsub', '-W', dependencyID, cvLaunch], stdout=subprocess.PIPE, universal_newlines=True)
		jobid4_str = jobid4.stdout
	else:
		print('[DEBUG] coverage_run.sh file written in foder: ')
		print(cvLaunch)
		print('[DEBUG] coverage_run.sh file contains:')
		print(cv_sh)
	


	###############
	# VarHound

	# pbs parameters
	select = 1
	ncpus = 2
	mem = '5g'

	pathStd = pbs_parameters(out_localApp, select, ncpus, mem, email, sendMode, name, queue, 'varhound')
	par = build_param_sh(pathStd)

	coverage_out = os.pathjoin(out_localApp, 'coverage')
	dr_cl = 'module load anaconda/3\n'
	dr_cl = dr_cl+'init bash\n'
	dr_cl = dr_cl+'source ~/.bashrc\n'
	dr_cl = dr_cl+'conda activate /data/hpc-data/shared/condaEnv/lianne\n'
	dr_cl = dr_cl+'cd '+out_localApp
	dr_cl = dr_cl+'\n'
	dr_cl = dr_cl+'\n'
	dr_cl = dr_cl+'cd '+LIANNE_FOLDER+'\n'
	dr_cl = dr_cl+'python3 VarHound/vhLaunch.py '+coverage_out



	varhound_file_run = os.path.join(out_localApp, 'varhound_run.sh')

	if debug is False:
		sh = open(varhound_file_run, 'w')
		sh.write(dr_cl)
		sh.close()
		dependencyID = 'depend=afterany:'+jobid4_str
		jobid5 = subprocess.run(['qsub', '-W', dependencyID, varhound_file_run], stdout=subprocess.PIPE, universal_newlines=True)
		jobid5_str = jobid5.stdout
	else:
		print('[DEBUG] varhound_run.sh file written in foder: ')
		print(varhound_file_run)
		print('[DEBUG] varhound_run.sh file contains:')
		print(dr_cl)


	
	os.sys.exit()
	
	################
	# BUILD CSV 
	print(samplesheet)
	# 
	# seq details
	
	make_seq_details.main(samplesheet)

	
	# build 
	# tmp_fastq

	################
	# 	




if __name__ == '__main__':
	# parser variable
	parser = argparse.ArgumentParser(description='Link Management System - Lianne')

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
						default = '128g',
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
	parser.add_argument('-d', '--debug', required=False,
						action='store_true',
						help='Run the script in debug mode\nNo jobs will be send\nNo file will be written - Default=False')


	args = parser.parse_args()
	runInput = args.runInput
	select = args.select
	ncpus = args.ncpus
	mem = args.mem
	email = args.email
	sendMode = args.sendMode
	name = args.name
	queue = args.queue
	debug = args.debug

	main(runInput, select, ncpus, mem, email, sendMode, name, queue, debug)