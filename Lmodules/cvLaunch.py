

#####################################
# NAME: cvLaunch.py.py
# AUTHOR: Luciano Giaco'
# Date: 03/02/2022
version = "0.1"
# ===================================

# Launch script for coverage
# It's required because it needs to parse 
# the bam file folder when the localApp finiched

import os
import argparse

LIANNE_FOLDER = '/data/hpc-data/shared/pipelines/lianne/'
COV_MODULE = os.path.join(LIANNE_FOLDER, 'Lmodules/coverage.py')

def main(dr_sh, out_localApp, debug):

	# write coverage sh
	
	coverage_file_run = os.path.join(out_localApp, 'coverage_run.sh')

	# retrieve bam file path for coverage analysis
	snv_bamDir = os.path.join(out_localApp, 'Logs_Intermediates/StitchedRealigned')
	bam_list = []
	for root, dirs, file in os.walk(snv_bamDir):
		for f in file:
			if f.endswith('.bam'):
				bam_file = os.path.join(root, f)
				bam_list.append(bam_file)

	if debug is False:
		# build sh file
		sh = open(coverage_file_run, 'w')
		sh.write(dr_sh)
		for b in bam_list:
			sh.write('python3 '+COV_MODULE+' -i '+b)
		sh.close()
		jobid2 = subprocess.run(['qsub', coverage_file_run], stdout=subprocess.PIPE, universal_newlines=True)
	else:
		print('[DEBUG] coverage_run.sh file written in foder: ')
		print(coverage_file_run)
		print('[DEBUG] coverage_run.sh file contains:')
		print(dr_sh)
		for b in bam_list:
			print('python3 '+COV_MODULE+' -i '+b)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Launch script for coverage - Lianne module')

	# arguments
	parser.add_argument('-p', '--shParameters', required=True,
						help='sh parameters built by Lianne')
	parser.add_argument('-o', '--outLocalApp', required=True,
						help='Output folder of Local App')
	parser.add_argument('-d', '--debug', required=False,
						action='store_true',
						help='Run the script in debug mode\nNo jobs will be send\nNo file will be written - Default=False')

	args = parser.parse_args()
	dr_sh = args.shParameters
	out_localApp = args.outLocalApp
	debug = args.debug

	main(dr_sh, out_localApp, debug)

