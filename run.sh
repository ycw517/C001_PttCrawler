#!/bin/bash
JOB_DIR=/home/pi/Project/C001_PttCrawler/
python3  ${JOB_DIR}MainJob.py 1 ${JOB_DIR}config.ini > /media/nfs/log/cronlog$(date +"%Y%m%d%H%M%S") 2>&1
