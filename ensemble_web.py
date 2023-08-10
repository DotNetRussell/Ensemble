#!/usr/bin/python3

from base64 import b64decode
import os
import re
import sys
import json
import uuid
import difflib
import argparse
import useraccess
import encryption
import ensemble_enums
import database_access
import ensemble_logging
import ensemble_constants

from difflib import Differ
from flask import Flask, redirect, request, render_template, jsonify, session, url_for
from ensemble_api import ensemble_api, set_session

parser = argparse.ArgumentParser(description="Ensemble Agent")
parser.add_argument("--debug", action=argparse.BooleanOptionalAction,
                    help="Puts the agent in debug mode where all logged events are outputed to console")

currentversion = 'v1.0.0 beta'

app = Flask(__name__)
app.register_blueprint(ensemble_api)

def check_logged_in():
    return ensemble_constants.USER_TOKEN in session


@app.route("/", methods=[ensemble_constants.GET, ensemble_constants.POST])
def home():
    if request.method == ensemble_constants.GET:
        if (check_logged_in()):
            return redirect(ensemble_constants.DASHBOARD_PATH)
        elif (useraccess.admin_user_exists() == True):
            return render_template(ensemble_constants.LOGIN_PAGE, version=currentversion)
        else:
            return render_template(ensemble_constants.CREATE_ADMIN_PAGE, title="Create Admin User", version=currentversion)

    elif request.method == ensemble_constants.POST:
        auth = request.authorization
        if auth:
            result = useraccess.log_user_in(
                auth.username.lower(), auth.password)
            if result == 0:
                return redirect(ensemble_constants.ROOT_WEB_DIR)
            elif result == 1:
                response = jsonify()
                session[ensemble_constants.USER_TOKEN] = auth.username.lower()
                session[ensemble_constants.CURRENT_WORKSPACE_ID_TOKEN] = 0
                set_session(session)
                response.headers[ensemble_constants.LOCATION_HEADER] = ensemble_constants.DASHBOARD_PATH
                response.autocorrect_location_header = False
                return response
            else:
                return redirect(ensemble_constants.ROOT_WEB_DIR)
        else:
            return redirect(ensemble_constants.ROOT_WEB_DIR)

def set_current_workspace(id):
    session[ensemble_constants.CURRENT_WORKSPACE_ID_TOKEN] = id


def get_current_workspace():
    workspaces = database_access.get_all_workspaces()
    if(len(workspaces)>0):
        currentWorkspace = None

        for workspace in workspaces:
            print(workspace)
            if int(workspace["Id"]) == int(session[ensemble_constants.CURRENT_WORKSPACE_ID_TOKEN]):
                currentWorkspace = workspace
                break
        return currentWorkspace
    else:
        return {}

@app.route(ensemble_constants.WORKSPACE_PATH, methods=[ensemble_constants.GET])
def workspace():
    if (check_logged_in()):
        if (len(request.args) > 0):
            workspaceName = request.args.get(ensemble_constants.ID_ARG, default=None, type=str)

            if workspaceName != None:
                database_access.create_workspace(workspaceName)

        return redirect(ensemble_constants.ROOT_WEB_DIR)
    else:
        return redirect(ensemble_constants.ROOT_WEB_DIR)


@app.route(ensemble_constants.DASHBOARD_PATH, methods=[ensemble_constants.GET])
def dashboard():
    if (check_logged_in()):
        if ensemble_constants.CURRENT_WORKSPACE_ID_TOKEN not in session:
            session[ensemble_constants.CURRENT_WORKSPACE_ID_TOKEN] = 0

        if (len(request.args) > 0):
            session[ensemble_constants.CURRENT_WORKSPACE_ID_TOKEN] = request.args.get(
                ensemble_constants.SET_WORKSPACE_ARG, default=1, type=int)

        currentWorkspaceId = session['currentWorkspaceId']
        dashboardViewModel = {
            'Agents': database_access.get_all_agents(),
            'AgentCount': database_access.get_active_agent_count(),
            'RunningJobs': database_access.get_running_job_count(currentWorkspaceId),
            'CompletedJobs': database_access.get_completed_job_count(currentWorkspaceId),
            'PendingJobs': database_access.get_pending_job_count(currentWorkspaceId),
            'CurrentWorkspace': get_current_workspace(),
            'Workspaces': database_access.get_all_workspaces()
        }
        currentworkspace = get_current_workspace()
        return render_template(ensemble_constants.DASHBOARD_PAGE, viewmodel=dashboardViewModel, currentworkspace=currentworkspace["Workspace"], version=currentversion)
    else:
        return redirect(ensemble_constants.ROOT_WEB_DIR)


@app.route(ensemble_constants.AGENT_HEALTH_PATH, methods=[ensemble_constants.GET])
def agenthealth():
    if (check_logged_in()):
        if (len(request.args) == 0):
            return redirect(ensemble_constants.AGENTS_PATH)
        else:
            id = request.args.get(ensemble_constants.ID_ARG, default=1, type=int)
            agent = database_access.get_agent_and_health_record_by_id(id)

            if (agent == None or len(agent) == 0):
                return redirect(ensemble_constants.ROOT_WEB_DIR)

            agentHealthViewModel = {
                'AgentId': agent['Id'],
                'AgentIpAddress': agent['IpAddress'],
                'MemoryUsed': agent['MemPct'],
                'ProcUsed': agent['CpuPct'],
                'StorageUsed': agent['StoragePct'],
                'LogSize': int(agent['LogSize']) / 1000,
                'JobData': agent['JobData'],
                'RunningProcesses' : agent['RunningProcesses']
            }
            return render_template(ensemble_constants.AGENT_HEALTH_PAGE, viewmodel=agentHealthViewModel, version=currentversion)
    else:
        return redirect('/')


@app.route(ensemble_constants.AGENTS_PATH, methods=[ensemble_constants.GET])
def agents():
    if (check_logged_in()):
        return render_template(ensemble_constants.AGENTS_PAGE, version=currentversion)
    else:
        return redirect(ensemble_constants.ROOT_WEB_DIR)

def sanitizeTarget(target):
    #some tools append a forward slash to a url in their output
    return target.strip() if len(target) > 0 and target[0] != '/' else target[1:len(target)].strip()

def extractTargets(jobResults):
    urlRegex = r'[http|ftp|https:\/\/]?[\w.-]*\.[\w]*'
    matches = re.findall(urlRegex, jobResults)
    targets = []
    for match in matches:
        match = sanitizeTarget(match)
        dbTarget = database_access.get_target_by_target(match.strip())

        # if we've recorded the target and it's been ignored
        # then don't return it as a target
        if(dbTarget is not None and dbTarget["Ignore"] == 1):
            continue

        target = {
            "Id" : len(targets),
            "Target": match,
            "AlreadyInDb": dbTarget is not None,
            "Ignored" : dbTarget is not None and dbTarget["Ignore"] == 1
        }

        # if target already exists in list then don't readd it
        if(any(x["Target"] == target["Target"] for x in targets)):
            continue

        targets.append(target)

    return targets

@app.route(ensemble_constants.SCHEDULED_JOB_RESULTS_PATH, methods=[ensemble_constants.GET])
def ScheduledJobResults():
	try:
		if check_logged_in():
			id = request.args.get(ensemble_constants.ID_ARG, default=1, type=int)
			jobResults = database_access.get_scheduled_job_results_by_scheduled_scheduled_job_id(session[ensemble_constants.CURRENT_WORKSPACE_ID_TOKEN],id)
			
			responseViewModel = []			
			for index in range(len(jobResults)):

				diff =  b64decode(jobResults[index]['jobResults']).decode('utf-8')
				if(index+1 < len(jobResults)):
					thisJob = b64decode(jobResults[index]['jobResults']).decode('utf-8') 
					previousJob = b64decode(jobResults[index+1]['jobResults']).decode('utf-8') 
					diff = '\n'.join(difflib.Differ().compare(thisJob.splitlines(), previousJob.splitlines()))

				responseViewModel.append({
					'AgentId':jobResults[index]['agentId'],
					'JobId':jobResults[index]['jobId'],
					'ScheduledJobId':jobResults[index]['scheduledJobId'],
					'JobRunDate':jobResults[index]['jobRunDateTime'],
					'JobDiff': diff
				})
                
			return render_template(ensemble_constants.SCHEDULED_JOB_RESULTS_PAGE, viewmodel=responseViewModel)
		else:			
			return redirect(ensemble_constants.ROOT_WEB_DIR)
	except Exception as error:
		ensemble_logging.log_message(f"{ensemble_constants.API_JOBS} failed with error {error}")	
		return redirect(ensemble_constants.ROOT_WEB_DIR)

@app.route(ensemble_constants.JOB_RESULTS_PATH, methods=[ensemble_constants.GET])
def jobresults():
    if (check_logged_in()):
        id = request.args.get(ensemble_constants.ID_ARG, default=1, type=str)
        jobData = database_access.get_job_result_by_id(id)

        if (len(jobData) == 0):
            return redirect(ensemble_constants.JOBS_PATH)

        jobs = []

        for job in jobData:
            jobResults = b64decode(job["JobResult"]).decode('utf-8')
            jobs.append({
                'JobId': job["JobId"],
                'AgentId': job["AgentId"],
                'JobResult': jobResults,
                'Targets': extractTargets(jobResults),
                'StartTime': job["StartTime"],
                'EndTime': job["FinishTime"],
                'WasCanceled': bool(job["WasCanceled"]),
                'Command':job["Command"],
                'Target': job["Target"]
            })

        jobResultsViewmodel = {
            "JobData": jobs
        }
        return render_template(ensemble_constants.JOB_RESULTS_PAGE, viewmodel=jobResultsViewmodel)
    else:
        return redirect(ensemble_constants.ROOT_WEB_DIR)


@app.route(ensemble_constants.SCHEDULED_JOBS_PATH, methods=[ensemble_constants.GET])
def scheduledJobs():
    if (check_logged_in()):        
        return render_template(ensemble_constants.SCHEDULED_JOBS_PAGE, version=currentversion)
    else:
        return redirect(ensemble_constants.ROOT_WEB_DIR)


@app.route(ensemble_constants.JOBS_PATH, methods=[ensemble_constants.GET])
def jobs():
    if (check_logged_in()):
        command = request.args.get(ensemble_constants.CMD_ARG, default=None, type=str)
        if(command is not None):
            if(ensemble_constants.CLEAR_COMPLETE_JOBS_COMMAND in command):
                for agent in database_access.get_all_agent_jobs():
                    database_access.insert_new_agent_command(agent["AgentId"], ensemble_constants.STOP_ALL_JOBS)
                database_access.clear_all_completed_jobs()
            elif(ensemble_constants.KILL_ALL_JOBS_COMMAND in command):
                for agent in database_access.get_all_agent_jobs():
                    database_access.insert_new_agent_command(agent["AgentId"], ensemble_constants.STOP_ALL_JOBS)
        return render_template(ensemble_constants.JOBS_PAGE, version=currentversion)
    else:
        return redirect(ensemble_constants.ROOT_WEB_DIR)


@app.route(ensemble_constants.AGENT_COMMANDS_PATH, methods=[ensemble_constants.POST])
def agentCommands():
    agentId = request.args.get(ensemble_constants.AGENT_ID_ARG, default=1, type=str)
    cmd = request.args.get(ensemble_constants.CMD_ARG, default=1, type=str)

    if ensemble_constants.STOP_ALL_JOBS in cmd or ensemble_constants.RESTART_AGENT in cmd or ensemble_constants.KILL_AGENT in cmd:
        database_access.complete_all_jobs_for_agent(agentId)

    database_access.insert_new_agent_command(agentId, cmd)
    return redirect(url_for(ensemble_constants.AGENT_HEALTH_PATH.replace("/",""), id=agentId))


@app.route(ensemble_constants.NEW_JOB_PATH, methods=[ensemble_constants.GET, ensemble_constants.POST])
def newjob():
    if check_logged_in():
        if request.method == ensemble_constants.GET:
            newjobViewModel = {
                    "CommandTemplates":database_access.get_all_command_template()
                }

            if len(request.args) > 0:
                jobId = request.args.get(ensemble_constants.DUPLICATE_ARG)
                job = database_access.get_job_by_id(jobId)

                newjobViewModel = {
                    "Command":job["Command"],
                    "Targets": '\n'.join(eval(job["Targets"])),
                    "IsSingleCommand":job["IsSingleCommand"],
                    "CommandTemplates":database_access.get_all_command_template()
                }

            return render_template(ensemble_constants.NEW_JOB_PAGE, viewmodel=newjobViewModel, version=currentversion)

        elif request.method == ensemble_constants.POST:
            rawJob = json.loads(request.form[ensemble_constants.JOB_DATA_ARG])

            if(bool(rawJob[ensemble_constants.SCHEDULED_JOB_ARG])):
                createNewScheduledJob(rawJob)
            else:
                createNewJob(rawJob)

            response = jsonify()
            response.headers[ensemble_constants.LOCATION_HEADER] = ensemble_constants.JOBS_PATH
            response.autocorrect_location_header = False

            return response
    else:
        return redirect(ensemble_constants.ROOT_WEB_DIR)

def createNewJob(rawJob):
    try:
        cmd = b64decode(rawJob[ensemble_constants.CMD_ARG]).decode(ensemble_constants.UTF8)
        targets = b64decode(rawJob[ensemble_constants.TARGETS_ARG]).decode(ensemble_constants.UTF8)
        isSingleCmd = bool(rawJob[ensemble_constants.SINGLE_COMMAND_ARG])
        loadBalancedCommand = bool(rawJob[ensemble_constants.IS_LOADBALANCED_ARG])
        if(str(cmd) == '' or len(targets) == 0):
            database_access.add_message({"MessageType":ensemble_enums.MessageType.WARNING.value, "Message": f"Failed to create job, missing fields"})
            return 
        job = {
            "Id": uuid.uuid4(),
            "Cmd": cmd,
            "Targets": targets.splitlines(),
            "IsSingleCmd": isSingleCmd,
            "IsLoadBalanced": loadBalancedCommand
        }

        database_access.queue_job_request(job)
        database_access.insert_workspace_job(session[ensemble_constants.CURRENT_WORKSPACE_ID_TOKEN], str(job["Id"]))
    except Exception as error:
        ensemble_logging.log_message(f"Error while attempting to create a new job failed with error {error}")

def createNewScheduledJob(rawJob):
    try:
        cmd = b64decode(rawJob[ensemble_constants.CMD_ARG]).decode(ensemble_constants.UTF8)
        targets = b64decode(rawJob[ensemble_constants.TARGETS_ARG]).decode(ensemble_constants.UTF8)
        isSingleCmd = bool(rawJob[ensemble_constants.SINGLE_COMMAND_ARG])
        loadBalancedCommand = bool(rawJob[ensemble_constants.IS_LOADBALANCED_ARG])
        runTime = str(rawJob[ensemble_constants.RUN_TIME_ARG])
        runDateTime = str(rawJob[ensemble_constants.RUN_DATE_TIME_ARG]).split(' GMT')[0]
        runType = int(rawJob[ensemble_constants.RUN_TYPE_ARG])
        workspaceId = session[ensemble_constants.CURRENT_WORKSPACE_ID_TOKEN]

        if(str(cmd) == '' or len(targets) == 0):
            database_access.add_message({"MessageType":ensemble_enums.MessageType.WARNING.value, "Message": f"Failed to create job, missing fields"})
            return 

        job = {
            "Id": uuid.uuid4(),
            "Cmd": cmd,
            "Targets": targets.splitlines(),
            "IsSingleCmd": isSingleCmd,
            "IsLoadBalanced": loadBalancedCommand,
            "RunTime": runTime,
            "RunDateTime": runDateTime,
            "RunType": runType,
            "WorkspaceId": workspaceId
        }

        database_access.insert_scheduled_job(job)

    except Exception as error:
        ensemble_logging.log_message(f"Error while attempting to create a new scheduled job failed with error {error}")

@app.route(ensemble_constants.STREAM_EVENTS_PATH, methods=[ensemble_constants.GET])
def StreamEvents():
    if check_logged_in():
        return render_template(ensemble_constants.STREAM_EVENTS_PAGE)
    else:
        return redirect(ensemble_constants.ROOT_WEB_DIR)

@app.route(ensemble_constants.MESSAGES_PATH, methods=[ensemble_constants.GET])
def messages():
    if check_logged_in():
        id = request.args.get(ensemble_constants.DISSMISS_ARG, default=None, type=str)
        if id != None:
            database_access.clear_message_by_id(id)
        response = jsonify(database_access.get_all_messages())
        return response
    else:
        return redirect(ensemble_constants.ROOT_WEB_DIR)

@app.route(ensemble_constants.SETTINGS_PATH, methods=[ensemble_constants.GET, ensemble_constants.POST])
def settings():

    if check_logged_in():
        settingsViewModel = {
            'Username': session[ensemble_constants.USER_TOKEN],
            'ConnectionString': encryption.get_agent_connection_string(APP_CONFIG[ensemble_constants.CONFIG_FILE_HOST_IP], APP_CONFIG[ensemble_constants.CONFIG_FILE_AGENT_REG_PORT])
        }
        return render_template(ensemble_constants.SETTINGS_PAGE, viewmodel=settingsViewModel, version=currentversion)
    else:
        return redirect(ensemble_constants.ROOT_WEB_DIR)


@app.route(ensemble_constants.LOGOUT_PATH, methods=[ensemble_constants.GET])
def logout():
    session.pop(ensemble_constants.USER_TOKEN, None)
    return redirect(ensemble_constants.ROOT_WEB_DIR)


args = parser.parse_args()
print(args)

ensemble_logging.initialize(ensemble_constants.WEB_LOG_FILENAME)
ensemble_logging.logLevel = 1
APP_CONFIG = json.loads(open("./.config.json", "r").read())

if (os.path.exists(ensemble_constants.WEB_LOGS_DIR) == False):
    os.popen(f"{ensemble_constants.MAKE_DIR_COMMAND} ./{ensemble_constants.WEB_LOGS_DIR}")
    ensemble_logging.log_message("Creating log directory")

# initialize the encryption lib with the key from the config or a new key
APP_CONFIG = encryption.initialize(APP_CONFIG)

database_access.initialize()

# will regenerate every time you restart the web server
# impact is all users will be logged out
secret = str(uuid.uuid4())

app.config.update(
    DEBUG=True,
    SECRET_KEY=secret,
    SESSION_COOKIE_HTTPONLY=True,
    REMEMBER_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Strict"
)

#from waitress import serve

app.run(debug=True, host='0.0.0.0', ssl_context=(ensemble_constants.CERT_PEM_FILENAME, ensemble_constants.KEY_PEM_FILENAME))

#at some point we'll switch to a production server
#currently waitress doesn't support tls naitively though
#serve(app, host='0.0.0.0', port=5000, url_scheme='https')