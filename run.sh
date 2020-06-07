#!/bin/bash
JOB_DIR=/home/pi/Project/C001_PttCrawler/
LOG_DIR=/home/pi/Project/C001_PttCrawler/
if [ -z "$1" ]
then
    LOG_DIR=/home/pi/Project/C001_PttCrawler/
else
    LOG_DIR=$1
fi
#python3  ${JOB_DIR}MainJob.py 1 ${JOB_DIR}config.ini > /media/nfs/log/cronlog$(date +"%Y%m%d%H%M%S") 2>&1
python3  ${JOB_DIR}MainJob.py 1 ${JOB_DIR}config.ini > ${LOG_DIR}cronlogpj 2>&1
