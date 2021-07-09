

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

    def __init__(self, pathStd, select, ncpus, mem, email, name, sendMode, queue):

        self.pathStdout = os.path.join(pathStd, 'stdout')
        self.pathStderr = os.path.join(pathStd, 'stderr')
        self.resources = 'select='+str(select)+':ncpus='+str(ncpus)+':mem='+str(mem)
        self.email = email
        # self.sendMode = sendMode
        self.name = name
        # self.queue = queue

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

def get_folderOut(input):
	head, tail = os.path.split(input)
	return(tail)

def main(input):
	tail = get_folderOut(input)
	print(tail)

	# Demultiplexing
	sendMode = 'ae'
	parameters = pbs_parameters(input, 1, 2, 10, 'luciano.giaco@policlinicogemelli.it', 'test', 'ae', 'workq')
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
	parser.add_argument('-i', '--input', required=True,
						help='NovaSeq output sequencing path')

	args = parser.parse_args()
	input = args.input


	main(input)