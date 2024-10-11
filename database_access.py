from datetime import datetime
from dateutil import parser

import sqlite3
import json
import ensemble_logging
import database_constants

class DatabaseConnection:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None

    def __enter__(self):
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            return self.connection
        except sqlite3.Error as error:
            ensemble_logging.log_message(f"Database connection failed: {error}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()

def initialize():
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.CREATE_WORKSPACE_TABLE_COMMAND())
            cursor.execute(database_constants.CREATE_WORKSPACE_JOB_TABLE_COMMAND())
            cursor.execute(database_constants.CREATE_AGENT_TABLE_COMMAND())
            cursor.execute(database_constants.CREATE_JOB_TABLE_COMMAND())
            cursor.execute(database_constants.CREATE_AGENT_JOB_TABLE_COMMAND())
            cursor.execute(database_constants.CREATE_JOB_RESULT_TABLE_COMMAND())
            cursor.execute(database_constants.CREATE_AGENT_HEALTH_TABLE_COMMAND())
            cursor.execute(database_constants.CREATE_USER_TABLE())
            cursor.execute(database_constants.CREATE_AGENT_COMMAND_TABLE())
            cursor.execute(database_constants.CREATE_MESSAGE_TABLE_COMMAND())
            cursor.execute(database_constants.CREATE_COMMAND_TEMPLATE_COMMAND())
            cursor.execute(database_constants.CREATE_TARGET_TABLE())
            cursor.execute(database_constants.CREATE_TARGET_JOB_TABLE())
            cursor.execute(database_constants.CREATE_STREAM_EVENT_TABLE_COMMAND())
            cursor.execute(database_constants.CREATE_SCHEDULED_JOB_TABLE())
            cursor.execute(database_constants.CREATE_SCHEDULED_JOB_RESULTS_MAPPING())

            cursor.execute(database_constants.INSERT_DEFAULT_WORKSPACE_COMMAND())
            cursor.execute(database_constants.INSERT_DEFAULT_COMMAND_TEMPLATES_COMMAND())
            db.commit()

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue creating tables")

def create_workspace(name):
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            command = database_constants.INSERT_WORKSPACE_COMMAND()
            cursor = db.cursor()
            cursor.execute(command, {'name': name})
            db.commit()

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue inserting workspace")


def insert_workspace_job(workspaceId, jobId):
    try:
            
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            ensemble_logging.log_message(
                f"Inserting Workspace Job {workspaceId} {jobId}")
            command = database_constants.INSERT_WORKSPACE_JOB_COMMAND()
            cursor = db.cursor()
            cursor.execute(command, {'workspaceId': str(
                workspaceId), 'jobId': str(jobId)})
            db.commit()

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue inserting workspace job")


def get_job_by_id(jobId):
    results = None
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.GET_JOB_BY_ID_COMMAND(), {
                        'jobId': jobId})
            rows = cursor.fetchall()
            for row in rows:
                results = {
                    "Id": row[0],
                    "JobId": row[1],
                    "Command": row[2],
                    "Targets": row[3],
                    "IsSingleCommand": row[4],
                    "IsJobStarted": row[5],
                    "IsJobCompleted": row[6]
                }

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue retrieving all workspaces")

    return results


def get_all_workspaces():
    results = []
    try:
        
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.GET_ALL_WORKSPACES())
            rows = cursor.fetchall()
            for row in rows:
                results.append({
                    "Id": row[0],
                    "Workspace": row[1]
                })

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue retrieving all workspaces")

    return results


def register_agent(agentIp):
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            registerCommand = database_constants.REGISTER_AGENT_COMMAND()
            setActiveCommand = database_constants.SET_AGENT_ACTIVE_COMMAND()
            cursor.execute(registerCommand, {'agentIp': agentIp})
            cursor.execute(setActiveCommand, {'agentIp': agentIp})
            db.commit()

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue inserting agent")


def get_agent_count():
    result = 0
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.GET_AGENT_COUNT_COMMAND())
            result = cursor.fetchall()[0][0]

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue retrieving agent count")

    return int(result)


def get_active_agent_count():
    result = 0
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.GET_ACTIVE_AGENT_COUNT_COMMAND())
            result = cursor.fetchall()[0][0]

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue retrieving agent count")

    return int(result)

def delete_command_template_by_id(id):
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.DELETE_COMMAND_TEMPLATE_COMMAND(),
            {
                'id': id 
            })
            db.commit()
    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue deleting command template")

def add_command_template(commandTemplate):
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            command = database_constants.INSERT_NEW_COMMAND_TEMPLATE_COMMAND()
            cursor = db.cursor()
            cursor.execute(command, {'commandDescription': str(commandTemplate["commandDescription"]), 'command': str(commandTemplate["command"])})
            db.commit()
    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue adding command template")

def get_all_command_template():
    commandTemplates = []
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.GET_ALL_COMMAND_TEMPLATE_COMMAND())
            rows = cursor.fetchall()
            for row in rows:
                commandTemplates.append({
                    "Id": row[0],
                    "CommandName": row[1],
                    "Command": row[2]
                })

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue retrieving all command templates")

    return commandTemplates

def remove_scheduled_job(id):
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.REMOVE_SCHEDULED_JOB_COMMAND(),
            {
                'scheduledJobId': id 
            })
            db.commit()

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue deleting scheduled job")

def get_scheduled_jobs_by_id():
    scheduledJobs = []
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.GET_ALL_UNRUN_JOBS_SCHEDULED_FOR_TODAY_COMMAND())
            rows = cursor.fetchall()
            for row in rows:
                scheduledJobs.append({
                    "id": row[0],
                    "cmd": row[1],
                    "runTime": row[2],                
                    "runDateTime": row[3],
                    "runType": row[4],
                    "targets": row[5],
                    "isSingleCmd": row[6],
                    "isLoadBalanced": row[7],
                    "workspaceId": row[8]
                })
    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue retrieving all scheduled jobs")
    finally:
        return scheduledJobs

def get_scheduled_job_results_by_scheduled_scheduled_job_id(workspaceId, scheduledJobId):
    scheduledJobs = []
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.GET_ALL_SCHEDULED_JOB_RESULTS_BY_SCHEDULED_JOB_ID(), { 'workspaceId':workspaceId, 'scheduledJobId':scheduledJobId })
            rows = cursor.fetchall()
            for row in rows:
                scheduledJobs.append({
                    "id": row[0],
                    "scheduledJobId": row[1],
                    "jobId": row[2],                
                    "jobRunDateTime": row[3],
                    "agentId": row[6],
                    "jobResults": row[7],
                    "startTime": row[8],
                    "finishTime": row[9]
                })
    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue retrieving all scheduled job results")
    finally:
        return scheduledJobs

def get_scheduled_job_results_by_scheduled_workspace_id(workspaceId):
    scheduledJobs = []
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.GET_ALL_SCHEDULED_JOB_RESULT_INFO(), {'workspaceId':workspaceId })
            rows = cursor.fetchall()
            for row in rows:
                scheduledJobs.append({
                    "id": row[0],
                    "scheduledJobId": row[1],
                    "jobId": row[2],                
                    "jobRunDateTime": row[3],
                    "agentId": row[6],
                    "jobResults": row[7],
                    "startTime": row[8],
                    "finishTime": row[9]
                })
    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue retrieving all scheduled job results")
    finally:
        return scheduledJobs

def insert_scheduled_job(scheduledJob):
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            command = database_constants.INSERT_SCHEDULED_JOB_COMMAND()
            cursor = db.cursor()
            
            runTime = str(scheduledJob["RunTime"])

            runDateTimeStr = str(scheduledJob["RunDateTime"])
            runDateTime = '' if runDateTimeStr == '' else parser.parse(runDateTimeStr)

            cursor.execute(command, {
                'cmd': str(scheduledJob["Cmd"]),
                'runTime': runTime,
                'runDateTime': runDateTime,
                'runType': int(scheduledJob["RunType"]),
                'targets': str(scheduledJob["Targets"]),
                'isSingleCmd': int(scheduledJob["IsSingleCmd"]),
                'isLoadBalanced': int(scheduledJob["IsLoadBalanced"]),
                "workspaceId": int(scheduledJob["WorkspaceId"])
            })

            db.commit()

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue inserting scheduled job")
         

def check_if_scheduled_job_exists(scheduledJobId):
    scheduledJobExists = False
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.GET_ALL_SCHEDULED_JOB_MAPPINGS_BY_ID_COMMAND(), {"scheduledJobId":scheduledJobId})
            scheduledJobExists = len(cursor.fetchall()) > 0
    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue checking if scheduled job exists")

    return scheduledJobExists


def insert_scheduled_job_mapping(scheduledJobMapping):
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            command = database_constants.INSERT_SCHEDULED_JOB_RESULTS_MAPPING()
            cursor = db.cursor()
            
            cursor.execute(command,{
                'scheduledJobId':  int(scheduledJobMapping["ScheduledJobId"]),
                'jobId': str(scheduledJobMapping["JobId"]),
                'jobRunTime': datetime.now()
            })
            db.commit()
    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue inserting scheduled job") 

def queue_job_request(job):
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            command = database_constants.INSERT_JOB_REQUEST_COMMAND()
            cursor = db.cursor()
            cursor.execute(command, {
                'jobId': str(job["Id"]),
                'cmd': job["Cmd"],
                'targets': str(job["Targets"]),
                'isSingleCommand': int(job["IsSingleCmd"]),
                'isLoadBalanced': int(job["IsLoadBalanced"])
            })
            db.commit()

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue inserting job")


def get_all_agents():
    agents = []
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.GET_ALL_ACTIVE_AGENTS())
            rows = cursor.fetchall()
            for row in rows:
                if (len(row) >= 4):
                    agents.append(
                        {
                            "Id": row[0],
                            "IpAddress": row[1],
                            "IsActive": row[2],
                            "LastActive": row[3]
                        }
                    )

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue retrieving all agents")

    return agents


def get_agent_and_health_record_by_id(agentId):
    result = None
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.GET_AGENT_AND_HEALTH_RECORD_BY_ID(), {
                        'agentId': agentId})
            row = cursor.fetchone()
            ensemble_logging.log_message(row)
            jobData = cursor.execute(database_constants.GET_AGENT_JOBS_BY_DAY(), {
                'agentId': agentId}).fetchall()
            ensemble_logging.log_message(jobData)
            jobDates = []
            for job in jobData:
                if (job[1] == None):
                    continue
                jobDates.append(
                    {'Count': job[0],
                        'Date': job[1]})

            result = {
                "Id": row[0],
                "IpAddress": row[1],
                "IsActive": row[2],
                "LastActive": row[3],
                "MemPct": row[6],
                "StoragePct": row[7],
                "CpuPct": row[8],
                "LastReportTime": row[9],
                "LogSize": 0 if row[10] == None or len(str(row[10])) == 0 else int(row[10])/1000,
                "JobData": jobDates,
                "RunningProcesses": row[11]
            }

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message(
            "Issue retrieving new agent by id and health records")

    return result


def get_all_agents_and_health_records():
    agents = []
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.GET_ALL_AGENTS_AND_HEALTH_RECORDS())
            rows = cursor.fetchall()
            for row in rows:

                command = database_constants.GET_ACTIVE_JOB_COUNT_BY_ID_COMMAND()
                cursor.execute(command, {'agentId': row[0]})
                activeJobCount = cursor.fetchone()

                agents.append({
                    "Id": row[0],
                    "IpAddress": row[1],
                    "IsActive": row[2],
                    "LastActive": row[3],
                    "MemPct": row[6],
                    "StoragePct": row[7],
                    "CpuPct": row[8],
                    "LastReportTime": row[9],
                    "ActiveJobCount": activeJobCount[0]
                }
                )

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue retrieving all agents with health")

    return agents


def check_for_new_jobs():
    result = []
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.GET_ALL_NEW_JOBS_COMMAND())
            result = cursor.fetchall()

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue retrieving new jobs")

    return result


def update_job_started(jobId):
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            command = database_constants.UPDATE_JOB_STARTED_COMMAND()
            cursor = db.cursor()
            cursor.execute(command, {'jobId': jobId})
            db.commit()

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue updating job start status")

def update_job_reset_job_status(jobId):
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            command = database_constants.UPDATE_JOB_RESET_JOB_STATUS_COMMAND()
            cursor = db.cursor()
            cursor.execute(command, {'jobId': jobId})
            db.commit()
    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue updating job reset status")


def get_agent_by_ip(agentIp):
    result = []
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            command = database_constants.GET_AGENT_BY_IP()
            cursor = db.cursor()
            cursor.execute(command, {'agentIp': agentIp})
            result = cursor.fetchall()

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue retrieving new jobs")

    if (len(result) == 1 and len(result[0]) >= 4):
        return {
            "Id": result[0][0],
            "IpAddress": result[0][1],
            "IsActive": result[0][2],
            "LastActive": result[0][3]
        }
    else:
        return None


def get_agent_by_id(agentId):
    result = []
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            command = database_constants.GET_AGENT_BY_ID()
            cursor = db.cursor()
            cursor.execute(command, {'agentId': agentId})
            result = cursor.fetchall()

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue retrieving new jobs")

    if (len(result) == 1 and len(result[0]) >= 4):
        return {
            "Id": result[0][0],
            "IpAddress": result[0][1],
            "IsActive": result[0][2],
            "LastActive": result[0][3]
        }
    else:
        return None


def clear_all_completed_jobs():
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.CLEAR_ALL_COMPLETED_JOBS_COMMAND())
            cursor.execute(
                database_constants.CLEAR_ALL_COMPLETED_JOB_RESULTS_COMMAND())
            db.commit()

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue clearing completed jobs")


def insert_new_agent_job_record(agentIp, jobId):
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            agent = get_agent_by_ip(agentIp)
            command = database_constants.INSERT_AGENT_JOB_COMMAND()
            cursor = db.cursor()
            cursor.execute(command, {'agentId': agent["Id"], 'jobId': jobId})
            db.commit()
            insert_new_job_result(jobId, agent["Id"])

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue inserting new agent job")


def insert_new_job_result(jobId, agentId):
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            command = database_constants.INSERT_JOB_RESULT_COMMAND()
            cursor = db.cursor()
            cursor.execute(command, {'agentId': agentId, 'jobId': jobId,
                        'startTime': ensemble_logging.get_date_time_now()})
            db.commit()

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue inserting new job result")

def update_scheduled_job_mapping_job_run_time(jobId):
    try:  
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:      
            cursor = db.cursor()        
            updateJobFinishedCommand = database_constants.UPDATE_SCHEDULED_JOB_MAPPING_RUN_TIME()
            cursor.execute(updateJobResultCommand, {'jobId': jobId, 'jobRunTime': datetime.now() })
            db.commit()

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue updating scheduled job run time")


def update_job_result(agentIp, jobId, result):
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            agent = get_agent_by_ip(agentIp)
            cursor = db.cursor()
            updateJobResultCommand = database_constants.UPDATE_JOB_RESULT_COMMAND()
            updateJobFinishedCommand = database_constants.UPDATE_JOB_FINISHED_COMMAND()
            cursor.execute(updateJobResultCommand, {'agentId': agent["Id"], 'jobId': jobId, 'result': result,
                        'finishTime': ensemble_logging.get_date_time_now(), 'wasCanceled': False})
            cursor.execute(updateJobFinishedCommand, {'jobId': jobId, })
            db.commit()

    except Exception as error:
        ensemble_logging.log_message(database_constants.UPDATE_JOB_RESULT_COMMAND(
            jobId, agent["Id"], result, ensemble_logging.get_date_time_now(), False))
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue updating job result")


def get_running_job_count(workspaceId):
    result = 0
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.GET_JOB_COUNT_COMMAND(), {
                        "workspaceId": workspaceId})
            result = cursor.fetchall()[0][0]

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue retrieving agent count")

    return int(result)


def get_pending_job_count(workspaceId):
    result = 0
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.GET_PENDING_JOB_COUNT_COMMAND(), {
                        "workspaceId": workspaceId})
            result = cursor.fetchall()[0][0]

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue retrieving agent count")

    return int(result)


def get_completed_job_count(workspaceId):
    result = 0
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.GET_COMPLETED_JOB_COUNT_COMMAND(), {
                        "workspaceId": workspaceId})
            result = cursor.fetchall()[0][0]

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue retrieving agent count")

    return int(result)


def get_job_result_by_id(id):
    results = []
    try:

        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            command = database_constants.GET_JOB_RESULT_BY_ID_COMMAND()
            cursor = db.cursor()
            cursor.execute(command, {'jobid': id})
            rows = cursor.fetchall()
            for row in rows:
                results.append({
                    "JobId": row[1],
                    "AgentId": row[2],
                    "JobResult": "" if row[3] == None else row[3],
                    "StartTime": row[4],
                    "FinishTime": row[5],
                    "WasCanceled": row[6],
                    "Command":row[7],
                    "Target":row[8]
                })

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue getting user by username")

    return results


def get_all_agent_jobs():
    result = []
    rows = []
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.GET_AGENT_JOBS())
            rows = cursor.fetchall()

            for row in rows:
                result.append({
                    "Id": row[1],
                    "AgentId": row[2],
                    "JobId": row[3]
                })

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue retrieving agent jobs")

    return result

def get_scheduled_jobs():
    scheduledJobs = []
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.GET_ALL_SCHEDULED_JOBS_COMMAND())
            rows = cursor.fetchall()
            for row in rows:
                scheduledJobs.append({
                    "id": row[0],
                    "cmd": row[1],
                    "runTime": row[2],                
                    "runDateTime": row[3],
                    "runType": row[4],
                    "targets": row[5],
                    "isSingleCmd": row[6],
                    "isLoadBalanced": row[7],
                    "workspaceId": row[8]
                })
    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue retrieving all scheduled jobs")
    finally:
        return scheduledJobs

def get_scheduled_jobs_by_workspace_id(workspaceId):
    scheduledJobs = []
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.GET_ALL_SCHEDULED_JOBS_BY_WORKSPACE_ID_COMMAND(),{"workspaceId":workspaceId})
            rows = cursor.fetchall()
            for row in rows:
                scheduledJobs.append({
                    "id": row[0],
                    "cmd": row[1],
                    "runTime": row[2],                
                    "runDateTime": row[3],
                    "runType": row[4],
                    "targets": row[5],
                    "isSingleCmd": row[6],
                    "isLoadBalanced": row[7],
                    "workspaceId": row[8]
                })
    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue retrieving all scheduled jobs")
    finally:
        return scheduledJobs

def get_all_jobs(workspaceId):
    result = []
    rows = []
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.GET_ALL_JOBS_BY_WORKSPACE_ID_COMMAND(), {
                        "workspaceId": workspaceId})
            rows = cursor.fetchall()

            for row in rows:
                result.append({
                    "Id":row[0],
                    "JobId": row[1],
                    "Cmd": row[2],
                    "Targets": row[3],
                    "IsSingleCmd": row[4],
                    "IsJobStarted": row[5],
                    "IsJobCompleted": row[6]
                })
    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue retrieving running jobs")

    return result


def get_all_running_jobs():
    result = []
    rows = []
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.GET_ALL_RUNNING_JOBS())
            rows = cursor.fetchall()

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue retrieving running jobs")

    for row in rows:
        if (len(row) == 3):
            result.append({
                "AgentIp": row[0],
                "JobId": row[1],
                "AgentId": row[2]
            })

    return result


def update_agent_health_status(agentHealth):
    try:

        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            reportTime = ensemble_logging.get_date_time_now()
            cursor = db.cursor()
            command = database_constants.UPSERT_AGENT_HEALTH_REPORT_COMMAND()
            cursor.execute(command, {'agentId': agentHealth["Id"], 'memPct': agentHealth["MemPct"], 'stgPct': agentHealth["StgPct"],
                        'cpuPct': agentHealth["CpuPct"], 'reportTime': reportTime, 'logSize': agentHealth["LogSize"], 'runningProcesses': agentHealth["RunningProcesses"]})

            db.commit()

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue updating agent health")


def get_user_by_username(username):
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            command = database_constants.GET_USER_BY_USERNAME_COMMAND()
            cursor = db.cursor()
            cursor.execute(command, {'uname': username})
            row = cursor.fetchone()

        if (len(row) == 4):
            return {
                "Id": row[0],
                "Username": row[1],
                "PasswordHash": row[2],
                "Salt": row[3]
            }
        else:
            return None

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue getting user by username")


def admin_user_check():
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.GET_ADMIN_USER_COUNT_COMMAND())
            row = cursor.fetchone()

            if (len(row) == 1 and int(row[0]) == 1):
                return True
            else:
                return False

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue checking for admin user")


def add_admin_user(username, passwordHashed, salt):
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.ADD_ADMIN_USER_COMMAND(), {
                        'uname': username, 'passhash': passwordHashed, 'salt': salt})
            db.commit()

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue inserting admin user")

def update_user_password(username, passwordHashed):
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.UPDATE_USER_PASSWORD_BY_USERNAME(),
                            {'uname':username, 'passhash':passwordHashed})
            db.commit()
    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue upating user password")

    

def insert_new_agent_command(agentId, command):
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.INSERT_AGENT_COMMAND_COMMAND(), {
                        'agentId': agentId, 'command': command, 'started': False, 'finished': False})
            db.commit()

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue inserting agent command")


def complete_all_agent_commands(agentId):
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.UPDATE_AGENT_COMMANDS_COMMAND(), {
                        'agentId': agentId})
            db.commit()

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue completing agent command")


def get_pending_agent_commands():
    result = []
    rows = []
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.GET_ALL_AGENT_COMMANDS())
            rows = cursor.fetchall()

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue retrieving pending agent commands")

    for row in rows:
        if (len(row) == 5):
            result.append({
                "Id": row[0],
                "AgentId": row[1],
                "Command": str(row[2])
            })

    return result


def complete_all_jobs_for_agent(agentId):
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            command = database_constants.UPDATE_JOB_FINISHED_BY_AGENT_ID_COMMAND()
            cursor = db.cursor()
            cursor.execute(command, {'agentId': agentId})
            db.commit()

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue setting all jobs to complete")


def add_message(message):
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            command = database_constants.INSERT_MESSAGE_COMMAND()
            cursor = db.cursor()
            cursor.execute(
                command, {'message_type': message["MessageType"], 'message': message["Message"]})
            db.commit()

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue inserting message")


def clear_all_messages():
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            command = database_constants.CLEAR_ALL_MESSAGES_COMMAND()
            cursor = db.cursor()
            cursor.execute(command)
            db.commit()

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue clearing message")


def clear_message_by_id(id):
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            command = database_constants.CLEAR_MESSAGE_BY_ID_COMMAND()
            cursor = db.cursor()
            cursor.execute(command, {'messageId': id})
            db.commit()

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue clearing message by id")


def set_agent_inactive(agentId):
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.SET_AGENT_INACTIVE_COMMAND(), {
                        'agentId': agentId})
            db.commit()

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue setting agent inactive")


def get_all_messages():
    result = []
    rows = []
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.GET_ALL_MESSAGES_COMMAND())
            rows = cursor.fetchall()

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue getting all messages")

    for row in rows:
        result.append({
            "Id": row[0],
            "MessageType": row[1],
            "Message": str(row[2])
        })

    return result


def insert_stream_event(event):
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            command = database_constants.INSERT_STREAM_EVENT_COMMAND()
            cursor = db.cursor()
            cursor.execute(command, {
                                        'eventId': event["EventId"],
                                        'event': event["Event"],
                                        'eventType': event["EventType"],
                                        'reportTime': ensemble_logging.get_date_time_now()
                                    })
            trim_command = database_constants.TRIM_STREAM_EVENT_TABLE_COMMAND()
            cursor.execute(trim_command)
            db.commit()

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue inserting stream event")


def get_all_stream_event():
    result = []
    rows = []
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.GET_ALL_STREAM_EVENTS_COMMAND())
            rows = cursor.fetchall()

            for row in rows:
                result.append({
                    "Id": row[0],
                    "EventId": row[1],
                    "Event": row[2],
                    "EventType": row[3],
                    "ReportTime": row[4]
                })

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue getting all stream events")

    return result

def insert_target(target):
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            command = database_constants.INSERT_TARGET_COMMAND()
            cursor = db.cursor()
            cursor.execute(command, { 'target': target.strip() })
            db.commit()

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue inserting target")

def insert_target_job(targetId,jobId):
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            command = database_constants.INSERT_TARGET_JOB_COMMAND()
            cursor = db.cursor()
            cursor.execute(command, { 'targetId': targetId, 'jobId': jobId })
            db.commit()

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue inserting target job")

def get_target_by_target(target):
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            command = database_constants.GET_TARGET_BY_TARGET_COMMAND()
            cursor = db.cursor()
            cursor.execute(command, {'target': target.strip()})
            row = cursor.fetchone()

            if(row == None):
                return None
            else:
                return {
                    "Id": row[0],
                    "Target": row[1],
                    "Ignore": row[2]
                }
    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue getting target by target")


def get_all_targets():
    result = []
    rows = []
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            cursor = db.cursor()
            cursor.execute(database_constants.GET_ALL_TARGET_COMMAND())
            rows = cursor.fetchall()

            for row in rows:
                result.append({
                    "Id": row[0],
                    "Target": row[1]
                })

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue getting all targets")

    return result

def ignore_target_by_target(target):
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            command = database_constants.IGNORE_TARGET_BY_TARGET_COMMAND()
            cursor = db.cursor()
            cursor.execute(command, { 'target': target })
            db.commit()

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue ignoring target by target")


def batch_ignore_target_by_target(targets):
    try:
        with DatabaseConnection(f"{database_constants.DATABASE_PATH}{database_constants.DATABASE_FILENAME}.sqlite3") as db:
            command = database_constants.BATCH_IGNORE_TARGET_BY_TARGETS_COMMAND()
            command += " ("
            counter = 1
            targetParameters = "{"
            for target in targets:
                command += ":"+str(counter)
                targetParameters += f""" "{str(counter)}" : "{str(target)}" """
                if(counter < len(targets)):
                    command += ","
                    targetParameters += ","
                counter += 1

            targetParameters += "}"
            command += ")"
            cursor = db.cursor()
            cursor.execute(command, json.loads(targetParameters))
            db.commit()

    except Exception as error:
        ensemble_logging.log_message(error)
        ensemble_logging.log_message("Issue ignoring target by target")
