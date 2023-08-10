#!/usr/bin/python3

import os
import json
import psutil
import socket
import base64
import argparse
import threading
import encryption
import subprocess
import communication
import ensemble_logging
import ensemble_constants

from subprocess import Popen, PIPE, STDOUT
#from crontab import CronTab
from datetime import datetime

parser = argparse.ArgumentParser(description="Ensemble Agent")
parser.add_argument("--debug", action=argparse.BooleanOptionalAction, help="Puts the agent in debug mode where all logged events are outputed to console")
parser.add_argument("--connection-string", required=True)

args = parser.parse_args()

ensemble_logging.initialize(ensemble_constants.AGENT_LOG_FILENAME)

if(args.debug != None):
	ensemble_logging.logLevel = 2

ENCRYPTION_KEY = ""
DIRECTOR_IP = ""
DIRECTOR_REGISTRATION_PORT = ""
lastHealthCheck = datetime.min

def initialize():
#	cron = CronTab(user='root')
#	job = cron.new(command=f'cd /root/Ensemble;/root/Ensemble/./ensemble_agent --connection-string \'{args.connection_string}\'')
#	job.every_reboot()
#	cron.write()

	if(os.path.isdir(ensemble_constants.LOGS_DIR) == False):
		run_command(f"{ensemble_constants.MAKE_DIR_COMMAND} ./{ensemble_constants.LOGS_DIR}")
	if(os.path.isdir(ensemble_constants.TEMP_DIR) == False):
		run_command(f"{ensemble_constants.MAKE_DIR_COMMAND} ./{ensemble_constants.TEMP_DIR}")
	if(os.path.isdir(ensemble_constants.JOB_RESULTS_DIR) == False):
		run_command(f"{ensemble_constants.MAKE_DIR_COMMAND} ./{ensemble_constants.JOB_RESULTS_DIR}")

	parse_connection_string()
	register_agent_with_director()

	threading.Thread(target=start_ensemble_agent_server).start()

	threading.Timer(60, check_if_still_connected).start()

def check_if_still_connected():
	if (datetime.now() - lastHealthCheck).total_seconds() / 60 > 60:
		ensemble_logging.log_message("Agent disconnected from director. Attempting to reregister")
		register_agent_with_director()
	threading.Timer(60, check_if_still_connected).start()

def parse_connection_string():
	ensemble_logging.log_message("Decoding connection string")
	connectionData = json.loads(args.connection_string)
	global ENCRYPTION_KEY
	global DIRECTOR_IP
	global DIRECTOR_REGISTRATION_PORT

	ENCRYPTION_KEY = connectionData["ENCRYPTION_KEY"].encode('utf-8')
	encryption.set_encryption_key(ENCRYPTION_KEY)

	DIRECTOR_IP = connectionData["HOST"]
	DIRECTOR_REGISTRATION_PORT = connectionData["PORT"]

	ensemble_logging.log_message("Connection string loaded")

def register_agent_with_director():
	message = "Agent Checking In"
	communication.tx(DIRECTOR_IP, int(DIRECTOR_REGISTRATION_PORT), encryption.encrypt_string(message))

def start_ensemble_agent_server():
	ensemble_logging.log_message("Starting Ensemble Agent Server")
	bindAddress = "0.0.0.0"
	bindPort = 5682
	serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	serverSocket.bind((bindAddress, bindPort))
	serverSocket.listen(100)

	while True:
		connection, address = serverSocket.accept()
		request = communication.EMPTY_BYTES
		while True:
			request += connection.recv(1024)
			if(communication.END_MARKER in request):
				request = communication.remove_end_marker(request)
				break

		ensemble_logging.log_message(f"Message Received {address}")
		ensemble_logging.log_message("Verifying sender IP Belongs to Director")
		if(address[0] == DIRECTOR_IP):
			threading.Thread(target=handle_api_request,args=(request,connection,)).start()
		else:
			ensemble_logging.log_message(f"Sender {address} is not director...Dumping message")

def handle_api_request(request,connection):
	ensemble_logging.log_message(f"Processing Request")
	decryptedRequest = encryption.decrypt_string(request)
	ensemble_logging.log_message(f"Decrypted Message {decryptedRequest}")
	lines = decryptedRequest.split("\\n")

	if(lines[0] == ensemble_constants.JOB_REQUEST and len(lines) == 2):
		ensemble_logging.log_message("Processing Job Request")
		process_job_request(lines[1].strip())
	elif(lines[0] == ensemble_constants.JOB_STATUS and len(lines) == 2):
		ensemble_logging.log_message("Processing Job Status Request")
		process_job_status_request(lines[1].strip(),connection)
	elif(lines[0] == ensemble_constants.JOB_RESULTS and len(lines) == 2):
		ensemble_logging.log_message("Processing Job Results Request")
		process_job_results_request(lines[1].strip(),connection)
	elif(lines[0] == ensemble_constants.JOB_CANCEL and len(lines) == 2):
		ensemble_logging.log_message("Processing Job Cancel Request")
		process_job_cancel_request(lines[1].strip())
	elif(lines[0] == ensemble_constants.HEALTH_REQUEST and len(lines) == 1):
		ensemble_logging.log_message("Processing Health Request")
		process_agent_health_request(connection)
	elif(lines[0] == ensemble_constants.CLEAR_LOGS and len(lines) == 1):
		ensemble_logging.log_message("Processing Clearing Logs Request")
		process_clear_agent_log_request()
	elif(lines[0] == ensemble_constants.KILL and len(lines) == 1):
		ensemble_logging.log_message("Processing Killing Agent Request")
		process_kill_agent_request()
	elif(lines[0] == ensemble_constants.RESTART and len(lines) == 1):
		ensemble_logging.log_message("Processing Restarting Agent Request")
		process_restart_agent_request()
	elif(lines[0] == ensemble_constants.STOP_JOBS and len(lines) == 1):
		ensemble_logging.log_message("Processing Killing Jobs Request")
		process_kill_jobs_request()

## Global Variables ##

threadPool={}
runningProcesses={}

#####################

def decode_payload(payload):
	ensemble_logging.log_message(f"Decoding JSON Payload {payload}")
	return json.loads(payload)

def run_command(command):
	return os.popen(command).read().strip()

def record_process_start(id,pid):
	ensemble_logging.log_message(f"Process {id} started")
	runningProcesses[id] = pid

def record_process_stop(id):
	ensemble_logging.log_message(f"Process {id} stopped")
	runningProcesses.pop(id)

def run_job_command(id,command):
	ensemble_logging.log_message(runningProcesses)
	ensemble_logging.log_message(f"Running Job Command: {command}")
	subprocessResult = None

	try:
		result = subprocess.Popen(command, stdout=PIPE, shell=True, stderr=STDOUT, bufsize=0, close_fds=True)
		record_process_start(id,result.pid)
		ensemble_logging.log_message(f"Process started with pid {result.pid}")
		resultText = ''
		for line in result.stdout.readlines():
			resultText = resultText + str(line.decode('UTF-8'))
		return resultText
	except Exception as error:
		return error

	finally:
		record_process_stop(id)	

def execute_single_command(job):
	ensemble_logging.log_message(f"Running Job ${job['Id']}")
	ensemble_logging.log_message(f"Running Command {job['Cmd']}")
	ensemble_logging.log_message(f"Targets {job['Targets']} ")
	command = job["Cmd"].replace("{{target}}",f"{ensemble_constants.TEMP_DIR}/{job['Id']}")
	jobResult = run_job_command(job["Id"],command)
	run_command(f"rm ./{ensemble_constants.TEMP_DIR}/{job['Id']}")
	threadPool.pop(job["Id"])
	ensemble_logging.log_job_completed(job)
	process_job_results(job,jobResult)

def execute_multi_command(job):
	ensemble_logging.log_message(f"Running Job ${job['Id']}")
	jobResult = ""
	for target in job["Targets"]:
		commandResult = run_job_command(job["Id"],job["Cmd"].replace("{{target}}",target))
		jobResult += str(commandResult)
	threadPool.pop(job["Id"])
	ensemble_logging.log_job_completed(job)
	process_job_results(job,jobResult)

def run_job(job):
	if(job["IsSingleCmd"]):
		ensemble_logging.log_message("Running single command")
		ensemble_logging.log_message("Stashing Targets")
		for target in job["Targets"]:
			ensemble_logging.log_message(f"Target {target}")
			run_command(f"echo {target} >> .temp/{job['Id']}")

		newJobThread = threading.Thread(target=execute_single_command,args=(job,))
		threadPool[job["Id"]]=newJobThread
		newJobThread.start()
	else:
		newJobThread = threading.Thread(target=execute_multi_command,args=(job,))
		threadPool[job["Id"]]=newJobThread
		newJobThread.start()

def process_job_request(jobJson):
	run_job(decode_payload(jobJson))

def process_job_results(job,jobResults):
	ensemble_logging.log_message(f"Processing job results for job {job['Id']}")
	encodedResults = base64.b64encode(jobResults.encode("utf-8")).decode("utf-8").strip()
	results = open(f"{ensemble_constants.JOB_RESULTS_DIR}/{job['Id']}", "a")
	results.write(encodedResults)
	results.close()

	if(args.debug != None):
		ensemble_logging.log_message(f"\r\n~~Job Completed~~\r\nID: {job['Id']}\r\nRESULTS: {jobResults}")

def process_job_status_request(jobId, connection):

	if(jobId in runningProcesses and jobId in threadPool):
		ensemble_logging.log_message(f"Job {jobId} Not Completed Yet")
		ensemble_logging.log_message("Encoding Status")
		response = encryption.encrypt_string("0")
		response += communication.END_MARKER
		ensemble_logging.log_message(f"Returning response to connection {connection}")

		connection.send(response)
	else:
		ensemble_logging.log_message(f"Job {jobId} Completed")
		ensemble_logging.log_message("Encoding Status")
		response = encryption.encrypt_string("1")
		response += communication.END_MARKER
		ensemble_logging.log_message(f"Returning response to connection {connection}")

		connection.send(response)

def process_job_results_request(jobId, connection):
	ensemble_logging.log_message(f"Checking for job {jobId} status")
	if(jobId not in runningProcesses and jobId not in threadPool):
		ensemble_logging.log_message(f"Job {jobId} completed")
		ensemble_logging.log_message(f"Checking for job {jobId} results")
		if(os.path.exists(f"{ensemble_constants.JOB_RESULTS_DIR}/{jobId}")):
			ensemble_logging.log_message(f"Job results found for job {jobId}")
			with open(f"{ensemble_constants.JOB_RESULTS_DIR}/{jobId}", "r") as results:
				ensemble_logging.log_message(f"Sending job {jobId} results to ensemble director")
				result = encryption.encrypt_string(results.read())
				result += communication.END_MARKER

				connection.send(result)

			run_command(f"rm {ensemble_constants.JOB_RESULTS_DIR}/{jobId}")

def process_job_cancel_request(jobId):
	ensemble_logging.log_message(f"Attempting to find job {jobId}")
	if(jobId in runningProcesses and jobId in threadPool):
		ensemble_logging.log_message(f"Job {jobId} found, attempting to cancel")
		threadPool[jobId].stop()
		threadPool.pop(jobId)
		runningProcesses.pop(jobId)

		jobStillRunning = jobId in threadPool or jobId in runningProcesses
		ensemble_logging.log_message(f"Job Canceled: {jobStillRunning}")

def process_agent_health_request(connection):
	global lastHealthCheck
	lastHealthCheck = datetime.now()

	meminfo = psutil.virtual_memory()
	storageinfo = psutil.disk_usage('/')
	cpuinfo = psutil.cpu_percent()
	logSize = run_command(ensemble_constants.STAT_COMMAND)
	runningProcesses = run_command(ensemble_constants.PROCESS_COMMAND)
	healthReport = {
		"MemInfo": meminfo,
		"StgInfo": storageinfo,
		"CpuInfo": cpuinfo,
		"LogSize": logSize,
		"RunningProcesses" : runningProcesses
	}

	ensemble_logging.log_message(f"Health Request Processed")
	ensemble_logging.log_message("Encoding Health Request")
	response = encryption.encrypt_string(json.dumps(healthReport))
	response += communication.END_MARKER
	ensemble_logging.log_message(f"Returning response to connection {connection}")

	connection.send(response)

def process_clear_agent_log_request():
	run_command(f"true > {ensemble_constants.LOGS_DIR}/{ensemble_constants.AGENT_LOG_FILENAME}")

def process_kill_agent_request():
	run_command(ensemble_constants.SHUTDOWN_COMMAND)

def process_restart_agent_request():
	run_command(ensemble_constants.REBOOT_COMMAND)

def process_kill_jobs_request():
	for id in runningProcesses:
		ensemble_logging.log_message(f"Killing pid {runningProcesses[id]}")
		run_command(f"{ensemble_constants.KILL_COMMAND} {runningProcesses[id]}")

initialize()
