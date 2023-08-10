#!/usr/bin/python3

import time
import json
import base64
import useraccess
import ensemble_enums
import database_access
import ensemble_logging
import ensemble_constants

from base64 import b64decode
from flask import Blueprint, jsonify, request

ensemble_logging.initialize(ensemble_constants.WEB_LOG_FILENAME)
ensemble_logging.logLevel = 1

ensemble_api = Blueprint('ensemble_api', __name__, template_folder='templates')
JSON_CONTENT_TYPE = {ensemble_constants.CONTENT_TYPE_HEADER:ensemble_constants.APPLICATION_JSON}
UNAUTHORIZED = "", ensemble_constants.UNAUTHORIZED, JSON_CONTENT_TYPE
SUCCESS = json.dumps({'success':True}), ensemble_constants.SUCCESS, JSON_CONTENT_TYPE
FAILED = json.dumps({'success':False}), ensemble_constants.SERVER_ERROR, JSON_CONTENT_TYPE

### HELPER FUNCTIONS ###

_session = []

def check_logged_in():
    return ensemble_constants.USER_TOKEN in _session

def set_session(session):
	global _session
	_session = session

##### API CALLS #####

@ensemble_api.route(ensemble_constants.API_LOGSTREAM, methods=[ensemble_constants.GET])
def LogStream():
	try:
		if check_logged_in():
			response = jsonify(database_access.get_all_stream_event())
			database_access.clear_all_messages()
			return response
		else:
			return UNAUTHORIZED
	except Exception as error:
		ensemble_logging.log_message(f"{ensemble_constants.API_LOGSTREAM} failed with error {error}")
		return FAILED

@ensemble_api.route(ensemble_constants.API_JOBS, methods=[ensemble_constants.GET])
def Jobs():
	try:
		if check_logged_in():
			response = jsonify(database_access.get_all_jobs(_session[ensemble_constants.CURRENT_WORKSPACE_ID_TOKEN]))
			return response
		else:
			return UNAUTHORIZED
	except Exception as error:
		ensemble_logging.log_message(f"{ensemble_constants.API_JOBS} failed with error {error}")
		return FAILED

@ensemble_api.route(ensemble_constants.API_SCHEDULED_JOB_RESULT_INFO, methods=[ensemble_constants.GET])
def ScheduledJobResultInfo():
	try:
		if check_logged_in():
			jobResults = database_access.get_scheduled_job_results_by_scheduled_workspace_id(_session[ensemble_constants.CURRENT_WORKSPACE_ID_TOKEN])
			
			responseViewModel = []			
			for jobResult in jobResults:
				responseViewModel.append({
					'AgentId':jobResult['agentId'],
					'JobId':jobResult['jobId'],
					'ScheduledJobId':jobResult['scheduledJobId'],
					'JobRunDate':jobResult['jobRunDateTime']
				})
				
			return responseViewModel
		else:
			return UNAUTHORIZED
	except Exception as error:
		ensemble_logging.log_message(f"{ensemble_constants.API_JOBS} failed with error {error}")
		return FAILED

@ensemble_api.route(ensemble_constants.API_SCHEDULED_JOBS, methods=[ensemble_constants.GET])
def ScheduledJobs():
	try:
		if check_logged_in():
			response = jsonify(database_access.get_scheduled_jobs_by_workspace_id(_session[ensemble_constants.CURRENT_WORKSPACE_ID_TOKEN]))
			return response
		else:
			return UNAUTHORIZED
	except Exception as error:
		ensemble_logging.log_message(f"{ensemble_constants.API_JOBS} failed with error {error}")
		return FAILED

@ensemble_api.route(ensemble_constants.API_AGENTS, methods=[ensemble_constants.GET])
def Agents():
	try:
		if check_logged_in():
			agents = []
			agentsData = database_access.get_all_agents_and_health_records()

			for agent in agentsData:
				memPct = float(agent['MemPct'])/100
				memHealthScore = 0
				if memPct <= .3:
					memHealthScore = .4
				elif memPct > .3 and memPct <= .6:
					memHealthScore = .2
				elif memPct > .6 <= .9:
					memHealthScore = .1
				else:
					memHealthScore = 0

				storagePct = float(agent['StoragePct'])/100
				storageHealthScore = 0
				if storagePct <= .3:
					storageHealthScore = .4
				elif storagePct > .3 and storagePct <= .6:
					storageHealthScore = .2
				elif storagePct > .6 <= .9:
					storageHealthScore = .1
				else:
					storageHealthScore = 0

				cpuPct = float(agent['CpuPct'])/100
				cpuHealthScore = 0
				if cpuPct <= .7:
					cpuHealthScore = .2
				elif cpuPct > .7 <= .9:
					cpuHealthScore = .1
				else:
					cpuHealthScore = 0

				agents.append({
					'Id': agent['Id'],
					'AgentIpAddress': agent['IpAddress'],
					'IsActive': bool(agent['IsActive']),
					'HealthPercent': float(memHealthScore + storageHealthScore + cpuHealthScore),
					'LastCheckinTime': agent['LastReportTime'],
					'ActiveJobCount': agent['ActiveJobCount']
				})
			response = jsonify(agents)
			return response
		else:
			return UNAUTHORIZED
	except Exception as error:
		ensemble_logging.log_message(f"{ensemble_constants.API_AGENTS} failed with error {error}")
		return FAILED


@ensemble_api.route(ensemble_constants.API_AGENT_HEALTH, methods=[ensemble_constants.GET])
def AgentHealth():
	try:
		if check_logged_in():
			id = request.args.get(ensemble_constants.ID_ARG, default=1, type=int)
			response = jsonify(database_access.get_agent_and_health_record_by_id(id))
			return response
		else:
			return UNAUTHORIZED
	except Exception as error:
		ensemble_logging.log_message(f"{ensemble_constants.API_AGENT_HEALTH} failed with error {error}")
		return FAILED


@ensemble_api.route(ensemble_constants.API_ADD_TARGET, methods=[ensemble_constants.GET, ensemble_constants.POST])
def AddTarget():
	try:
		if check_logged_in():

			if request.method == ensemble_constants.GET:
				target = request.args.get(ensemble_constants.TARGET_ARG, default="", type=str)
				database_access.insert_target(target)
				database_access.add_message({"MessageType":ensemble_enums.MessageType.NOTIFICATION.value, "Message": f"{target} added to targets list"})

			elif request.method == ensemble_constants.POST:
				data = request.data
				targets = json.loads(data)

				for target in targets:
					targetExists = database_access.get_target_by_target(target)
					if(targetExists is None):
						database_access.insert_target(target)
						
			return SUCCESS
		else:
			return UNAUTHORIZED
	except Exception as error:
		ensemble_logging.log_message(f"{ensemble_constants.API_ADD_TARGET} failed with error {error}")
		return FAILED


@ensemble_api.route(ensemble_constants.API_REMOVE_TARGET, methods=[ensemble_constants.GET, ensemble_constants.POST])
def RemoveTarget():
	try:
		if check_logged_in():
			if request.method == ensemble_constants.GET:
				target = request.args.get(ensemble_constants.TARGET_ARG, default="", type=str)

				targetExists = database_access.get_target_by_target(target)
				if(targetExists is None):
					database_access.insert_target(target)

				database_access.ignore_target_by_target(target)
				database_access.add_message({"MessageType":ensemble_enums.MessageType.NOTIFICATION.value, "Message": f"{target} removed from targets list"})

			elif request.method == ensemble_constants.POST:
				data = request.data
				targets = json.loads(data)

				for target in targets:
					targetExists = database_access.get_target_by_target(target)
					if(targetExists is None):
						database_access.insert_target(target)
						
				database_access.batch_ignore_target_by_target(targets)
				
			return SUCCESS
		else:
			return UNAUTHORIZED
	except Exception as error:
		ensemble_logging.log_message(f"{ensemble_constants.API_ADD_TARGET} failed with error {error}")
		return FAILED

@ensemble_api.route(ensemble_constants.API_UPDATE_PASSWORD, methods=[ensemble_constants.POST])
def UpdatePassword():
	try:
		if check_logged_in():
			passwordJson = json.loads(request.data)
			oldPass = passwordJson["old"]
			newPass = passwordJson["new"]
			
			sessionUsername = _session[ensemble_constants.USER_TOKEN]
			user = database_access.get_user_by_username(sessionUsername)
			
			hashedPassword = useraccess.salt_password(oldPass, user['Salt'])

			if(hashedPassword == user['PasswordHash']):
				database_access.update_user_password(sessionUsername, useraccess.salt_password(newPass, user['Salt']))
				return SUCCESS
			else:
				return UNAUTHORIZED
		else:
			return UNAUTHORIZED

	except Exception as error:
		ensemble_logging.log_message(f"{ensemble_constants.API_UPDATE_PASSWORD} failed with error {error}")
		return FAILED

@ensemble_api.route(ensemble_constants.API_GET_SERVER_TIME, methods=[ensemble_constants.GET])
def getTime():
	if check_logged_in():
		return time.strftime('%H:%M:%S')
	else:
		return UNAUTHORIZED

@ensemble_api.route(ensemble_constants.API_GET_COMMAND_TEMPLATES, methods=[ensemble_constants.GET])
def getCommandTemplates():
	try:
		if check_logged_in():
			return jsonify(database_access.get_all_command_template())
		else:
			return UNAUTHORIZED
	except Exception as error:
		return UNAUTHORIZED

@ensemble_api.route(ensemble_constants.API_ADD_COMMAND_TEMPLATES, methods=[ensemble_constants.POST])
def addCommandTemplates():
	try:
		if check_logged_in() and request.method == ensemble_constants.POST:
			commandTemplate = json.loads(request.data)
			database_access.add_command_template(commandTemplate)
			return SUCCESS
		else:
			return UNAUTHORIZED
	except Exception as error:
		return UNAUTHORIZED


@ensemble_api.route(ensemble_constants.API_DELETE_COMMAND_TEMPLATES, methods=[ensemble_constants.GET])
def deleteCommandTemplates():
	try:
		if check_logged_in():
			commandTemplateId = request.args.get(ensemble_constants.ID_ARG, default="", type=int)
			database_access.delete_command_template_by_id(commandTemplateId)
			return SUCCESS
		else:
			return UNAUTHORIZED
	except Exception as error:
		return UNAUTHORIZED

@ensemble_api.route(ensemble_constants.API_DELETE_SCHEDULED_JOB, methods=[ensemble_constants.GET])
def deleteScheduledJob():
	if check_logged_in():
		if request.method == ensemble_constants.GET:
			target = request.args.get(ensemble_constants.ID_ARG, default="", type=str)
			if(target != ''):
				database_access.remove_scheduled_job(target)
		return SUCCESS	
	else:
		return UNAUTHORIZED