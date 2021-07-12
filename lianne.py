

#####################################
# NAME: lianne.py
# AUTHOR: Luciano Giaco'
# Date: 06/07/2021
version = "0.1"
# ===================================


import os
import argparse
from jinja2 import Template


RESULTS = '/data/novaseq/Diagnostic/NovaSeq/Results/'
TMP = '/data/novaseq/Diagnostic/NovaSeq/Results/tmp'


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

    def sendMode(self):
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

def main(runInput, select, ncpus, mem, email, sendMode, queue):
	tail = get_folderOut(runInput)
	print(tail)

	################
	# DEMULTIPLEXING

	# pbs parameters
	
	parameters = pbs_parameters(runInput, select, ncpus, mem, email, sendMode, name, queue)
	print(parameters.getStdout())
# 	tm = Template("#PBS -o {{ per.getStdout() }}\n\
# #PBS -e {{ per.getStderr() }}\n\
# #PBS -M {{ per.getEmail() }}\n\
# #PBS -m {{ per.name() }}\n\
# #PBS -l {{ per.getResources() }}")
# 	msg = tm.render(per=parameters)

	# print(msg)
	

#PBS -N {{ per.getName() }}\n\
#PBS -q {{ per.getQueue() }}\n\

if __name__ == '__main__':
	# parser variable
	parser = argparse.ArgumentParser(description='Lims Management System - Lianne')

	# arguments
	parser.add_argument('-i', '--runInput', required=True,
						help='NovaSeq output sequencing path')
	parser.add_argument('-l1', '--select', required=False,
						default = 1,
						help='Select the number of chunks to send on PBS cluser - Default=1')
	parser.add_argument('-l2', '--ncpus', required=False,
						default = 24,
						help='Select the number of ncpus to require - Default=24')
	parser.add_argument('-l3', '--mem', required=False,
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

	main(runInput, select, ncpus, mem, email, sendMode, queue)