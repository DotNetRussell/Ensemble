#!/usr/bin/python3

import os
import sys
import ensemble_constants

from datetime import datetime

logLevel = 1
logConsumer = ensemble_constants.DIRECTOR_LOG_FILENAME

def initialize(consumer):
    global logConsumer
    logConsumer = consumer

def log_message(text):
    timeStamp = get_date_time_now()
    if(logLevel == 1):
        os.popen(f"{ensemble_constants.ECHO_COMMAND} '{timeStamp}: {text}' >> {ensemble_constants.LOGS_DIR}/{logConsumer}")
    elif(logLevel == 2):
        print(f"{timeStamp}: {text}", file=sys.stdout)
            
def log_job(job):
    jobString = ""
    jobString += f"Job ID: {job['Id']}"
    jobString += f"Job CMD: {job['Cmd']}"
    jobString += f"Job Targets: {job['Targets']}"
    jobString += f"Job Run In Single Command: {job['IsSingleCmd']}"
    log_message(jobString)

def log_job_completed(job):
    log_message(f"Job Completed: {job['Id']}")

def get_date_time_now():
    return datetime.fromtimestamp(datetime.now().timestamp())