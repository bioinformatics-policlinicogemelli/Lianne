# LIANNE

***LInk mANagemenNt systEm*** 

This application manage the Bioinformatic workflow for **"Programma di profilazione genomica dei tumori FPG500**

It's designed for the analysis of panel Illumina TruSight Oncology 500 sequenced using the Illumina Novaseq6000 sequencer

Lianne manage 
## Usage


```
usage: lianne.py [-h] -i RUNINPUT [-l1 SELECT] [-l2 NCPUS] [-l3 MEM]
                 [-e EMAIL] [-m SENDMODE] [-N NAME] [-q QUEUE]

Link Management System - Lianne

optional arguments:
  -h, --help            show this help message and exit
  -i RUNINPUT, --runInput RUNINPUT
                        NovaSeq output sequencing path
  -l1 SELECT, --select SELECT
                        Select the number of chunks to send on PBS cluser -
                        Default=1
  -l2 NCPUS, --ncpus NCPUS
                        Select the number of ncpus to require - Default=24
  -l3 MEM, --mem MEM    Select the amount of memory to require - Default=128
  -e EMAIL, --email EMAIL
                        Insert the email -
                        Default=luciano.giaco@policlinicogemelli.it
  -m SENDMODE, --sendMode SENDMODE
                        Insert the sending email mode - Default=ae
  -N NAME, --name NAME  Insert the job name - Default=lianne
  -q QUEUE, --queue QUEUE
                        Insert the queue to send job - Default=workq
```




