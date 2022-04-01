# LIANNE

***LInk mANagemenNt systEm*** 

This application manage the Bioinformatic workflow for **"Programma di profilazione genomica dei tumori FPG500**

It's designed for the analysis of panel Illumina TruSight Oncology 500 sequenced using the Illumina Novaseq6000 sequencer.

The Variant calling is performed using Illumina Local App and uploaded on PierianDX Clinical Genomics Workspace (CGW) for the variant interpretation.
For these steps is compulsory to have an agreement with Illumina for the Lacal App usage and a licensed account on PierianDX.

It is also use Lianne for coverage analysis using only the analysis coverage jobs 

All sh scripts are designed for PBS scheduler, if it doesn't available on your system the scripts can be used deleting the PBS parameters part



## Requirements

### Conda

Lianne System works in Conda environment, to install Conda follow: 

The conda packages to install are listed in *conda_packages_list.txt*

### Singularity

It also use **Singularity v3.7.4** for the Illumina Local App


### VarHound

The coverage analysis use VarHound available on GitHub at:

`https://github.com/fernandoPalluzzi/VarHound`





## Usage

### First usage

Insert the absolute path of the confPath.ini file in the CONF variable at the beginnign of the lianne.py file.

```
CONF = absolutePath/confPath.ini
```


```
usage: lianne.py [-h] -i RUNINPUT [-l1 SELECT] [-l2 NCPUS] [-l3 MEM]
                 [-e EMAIL] [-m SENDMODE] [-N NAME] [-q QUEUE]

Link Management System - Lianne

optional arguments:
  -h, --help            show this help message and exit
  -i RUNINPUT, --runInput RUNINPUT
                        NovaSeq output sequencing path
  -l_select SELECT, --select SELECT
                        Select the number of chunks to send on PBS cluser -
                        Default=1
  -l_ncpus NCPUS, --ncpus NCPUS
                        Select the number of ncpus to require - Default=24
  -l_mem MEM, --mem MEM
                        Select the amount of memory to require - Default=128
  -e EMAIL, --email EMAIL
                        Insert the email -
                        Default=luciano.giaco@policlinicogemelli.it
  -m SENDMODE, --sendMode SENDMODE
                        Insert the sending email mode - Default=ae
  -N NAME, --name NAME  Insert the job name - Default=lianne
  -q QUEUE, --queue QUEUE
                        Insert the queue to send job - Default=workq
  -d, --debug           Run the script in debug mode No jobs will be send No
                        file will be written - Default=False
  -f, --fastqc          Perform FastQC analysis on fastq files - Default=False
```

## Steps

Starting Lianne using the default parameters the scrit needs only the path folder of sequencer output.


### Demultiplexing

The demultiplexing results are stored in a temporary folder with the following name *analysis_runName* where runName is the name of sequencing output folder

Lianne performs:

1. A check if the samplesheet exists. If the samplesheet not exists, Lianne returns a warning and exit. If the samplesheet has another name, Lianne makes a copy in the temporary using **SampleSheet.csv as file name**

2. Sends the demultiplexing job using Illumina TruSight Oncology 500 Local App with the following command line:

```
#! /bin/bash 

#PBS -o /temporaryFolder/analysis_runName/stdout_demultiplex
#PBS -e /temporaryFolder/analysis_runName/stderr_demultiplex
#PBS -l select=1:ncpus=24:mem=128g
#PBS -M your@email.com
#PBS -m ae
#PBS -N lianne_demultiplex
#PBS -q workq

module load singularity/3.7.4
module load openmpi/4.1.1
cd /apps/trusight/2.2.0

./TruSight_Oncology_500_RUO.sh \
--analysisFolder /temporaryFolder/analysis_runName/runName \
--resourcesFolder /apps/trusight/2.2.0/resources \
--runFolder /data/novaseq/Diagnostic/NovaSeq/SequencerOutput/runName \
--engine singularity \
--sampleSheet /temporaryFolder/analysis_runName/SampleSheet.csv \
--isNovaSeq \
--demultiplexOnly
```


### Local App

The Illumina TruSigth Oncology Local App v2.2.0 is used for the local variant calling analysis.

Lianne sends in queue the Local App using a sh script containing the following command line and PBS parameters:

```
#! /bin/bash 

#PBS -o /data/novaseq_results/runName/stdout_LocalApp
#PBS -e /data/novaseq_results/runName/stderr_LocalApp
#PBS -l select=2:ncpus=24:mem=128g
#PBS -M your@email.com
#PBS -m ae
#PBS -N lianne_LocalApp
#PBS -q workq

module load singularity/3.7.4
module load openmpi/4.1.1
cd /apps/trusight/2.2.0

./TruSight_Oncology_500_RUO.sh \
--analysisFolder /data/novaseq_results/runName \
--resourcesFolder /apps/trusight/2.2.0/resources \
--runFolder /data/novaseq/Diagnostic/NovaSeq/SequencerOutput/runName \
--engine singularity \
--sampleSheet /temporaryFolder/analysis_runName/SampleSheet.csv \
--isNovaSeq
```



