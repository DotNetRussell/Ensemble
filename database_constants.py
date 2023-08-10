from datetime import datetime

DATABASE_PATH = "./"
DATABASE_FILENAME = ".ensemble_database"


######################CREATE TABLES###########################

def CREATE_COMMAND_TEMPLATE_COMMAND():
    return  """ CREATE TABLE IF NOT EXISTS command_template(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command_name_short STRING UNIQUE,
                command STRING)
            """

def CREATE_WORKSPACE_TABLE_COMMAND():
    return """  CREATE TABLE IF NOT EXISTS workspace(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name STRING UNIQUE)
            """

def CREATE_WORKSPACE_JOB_TABLE_COMMAND():
    return """  CREATE TABLE IF NOT EXISTS workspace_job(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id STRING,
                job_id STRING)
            """

def CREATE_MESSAGE_TABLE_COMMAND():
    return  """
                CREATE TABLE IF NOT EXISTS message(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_type INT,
                message STRING)
            """

def CREATE_AGENT_TABLE_COMMAND():
    return """  CREATE TABLE IF NOT EXISTS agent(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT UNIQUE,
                is_active BOOL,
                last_active DATETIME)
            """

def CREATE_JOB_TABLE_COMMAND():
    return """  CREATE TABLE IF NOT EXISTS job(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id STRING,
                cmd TEXT,
                targets STRING,
                is_single_cmd BOOL,
                job_started BOOL,
                job_completed BOOL,
                is_load_balanced BOOL)
            """

def CREATE_AGENT_JOB_TABLE_COMMAND():
    return """  CREATE TABLE IF NOT EXISTS agent_job(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id STRING,
                job_id STRING)
            """

def CREATE_JOB_RESULT_TABLE_COMMAND():
    return """  CREATE TABLE IF NOT EXISTS job_result(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id STRING,
                agent_id STRING,
                job_result BLOB,
                start_time DATETIME,
                finish_time DATETIME,
                was_canceled BOOL)
            """

def CREATE_AGENT_HEALTH_TABLE_COMMAND():
    return """  CREATE TABLE IF NOT EXISTS agent_health(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id STRING unique,
                memory_percent REAL,
                storage_percent REAL,
                cpu_percent REAL,
                report_time DATETIME,
                log_size INTEGER,
                running_processes TEXT)
            """

def CREATE_USER_TABLE():
    return  """ CREATE TABLE IF NOT EXISTS user(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username STRING unique,
                passwordhash STRING,
                salt STRING unique)
            """

def CREATE_AGENT_COMMAND_TABLE():
    return  """ CREATE TABLE IF NOT EXISTS agent_command(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id STRING,
                command STRING,
                command_started BOOL,
                command_finished BOOL)
            """

def CREATE_STREAM_EVENT_TABLE_COMMAND():
    return  """ CREATE TABLE IF NOT EXISTS stream_event(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id STRING,
                event BLOB,
                event_type INT,
                report_time DATETIME)
            """

def CREATE_TARGET_TABLE():
    return  """ CREATE TABLE IF NOT EXISTS target(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target STRING UNIQUE,
                ignore BOOL)
            """

def CREATE_TARGET_JOB_TABLE():
    return  """ CREATE TABLE IF NOT EXISTS target_job(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_id INTEGER,
                job_id STRING)
            """

def CREATE_SCHEDULED_JOB_TABLE():
    return  """ CREATE TABLE IF NOT EXISTS scheduled_job(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cmd TEXT,
                run_time STRING,
                run_date_time DATETIME,
                run_type INTEGER,
                targets STRING,
                is_single_cmd BOOL,
                is_load_balanced BOOL,                
                workspace_id INTEGER)                
            """

def CREATE_SCHEDULED_JOB_RESULTS_MAPPING():
    return  """ CREATE TABLE IF NOT EXISTS scheduled_job_results_mapping(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scheduled_job_id INTEGER,
                job_id STRING,
                job_run_date_time DATETIME)
            """

##############################################################################

########################## INSERT ROWS #######################################

def INSERT_SCHEDULED_JOB_COMMAND():
    return  """ 
                INSERT OR IGNORE INTO scheduled_job(id, cmd, run_time, run_date_time, run_type, targets, is_single_cmd, is_load_balanced, workspace_id)
                VALUES(NULL, :cmd, :runTime, :runDateTime, :runType, :targets, :isSingleCmd, :isLoadBalanced, :workspaceId)
            """

def INSERT_SCHEDULED_JOB_RESULTS_MAPPING():
    return  """ 
                INSERT OR IGNORE INTO scheduled_job_results_mapping(id, scheduled_job_id, job_id, job_run_date_time)
                VALUES(NULL, :scheduledJobId, :jobId, :jobRunTime)
            """

def INSERT_TARGET_COMMAND():
    return  """
                INSERT OR IGNORE INTO target(id,target, ignore)
                VALUES(NULL,:target, False)
            """

def INSERT_TARGET_JOB_COMMAND():
    return  """
                INSERT INTO target_job(id,target_id,job_id)
                VALUES(NULL, :targetId, :jobId)
            """

def INSERT_STREAM_EVENT_COMMAND():
    return  """
                INSERT INTO stream_event(id, event_id, event, event_type, report_time)
                VALUES (NULL, :eventId, :event, :eventType, :reportTime)
            """

def INSERT_DEFAULT_COMMAND_TEMPLATES_COMMAND():
    return  """
                INSERT OR IGNORE INTO command_template (id,command_name_short,command)
                VALUES  (NULL,"nikto","nikto -h {{target}}"),
                        (NULL,"nmap script scan all ports", "nmap -p- -sC {{target}}" ),
                        (NULL,"nmap ping scan for up hosts. Results in grepable format and unique", "nmap -sP -iL {{target}} -oG results > /dev/null && cat results | sort -u;"),
                        (NULL,"nmap scan open ports", "nmap -p- --open {{target}}" ),
                        (NULL,"wpscan", "wpscan --format cli-no-color --update --url {{target}}" ),
                        (NULL,"dirb","dirb {{target}} /usr/share/wordlists/"),
                        (NULL,"wfuzz","wfuzz --hc 404,301 -w /usr/share/wordlists/ {{target}}/FUZZ"),
                        (NULL,"sublist3r", "sublist3r -n -d {{target}}"),
                        (NULL,"ping", "ping -c 1 {{target}}"),
                        (NULL,"curl", "curl --verbose {{target}}"),
                        (NULL,"amass intel org", "amass intel -org '{{target}}'"),
                        (NULL,"amass intel org", "amass intel -d {{target}} -whois"),
                        (NULL,"amass enum", "amass enum -nocolor -d {{target}}"),
                        (NULL,"amass enum brute", "amass -nocolor enum -brute -d {{target}}"),
                        (NULL,"amass enum ip", "amass enum -nocolor -ip -d {{target}}"),
                        (NULL,"amass enum subdomains", "amass enum -passive -nocolor -ip -src -d {{target}}")
            """

def INSERT_NEW_COMMAND_TEMPLATE_COMMAND():
    return  """
                INSERT OR IGNORE INTO command_template(id,command_name_short,command)
                VALUES(NULL,:commandDescription,:command)
            """

def INSERT_MESSAGE_COMMAND():
    return  """
                INSERT INTO message (id,message_type,message)
                VALUES(NULL,:message_type,:message)
            """

def INSERT_DEFAULT_WORKSPACE_COMMAND():
    return  """
                INSERT OR IGNORE INTO workspace (id, name)
                VALUES(0,"Default")
            """

def ADD_ADMIN_USER_COMMAND():
    return  """
                INSERT INTO user (id,username,passwordhash,salt)
                VALUES(NULL,:uname,:passhash,:salt)
            """

def REGISTER_AGENT_COMMAND():
    return f"""
                INSERT OR IGNORE INTO agent (id,ip_address,is_active,last_active)
                VALUES(NULL,:agentIp,1,"{datetime.now()}")
            """

def INSERT_WORKSPACE_COMMAND():
    return """
                INSERT OR IGNORE INTO workspace (id,name)
                VALUES(NULL,:name)
            """

def INSERT_WORKSPACE_JOB_COMMAND():
    return  """
                INSERT INTO workspace_job (id, workspace_id, job_id)
                VALUES(NULL, :workspaceId, :jobId)
            """

def INSERT_JOB_REQUEST_COMMAND():
    return """
                INSERT INTO job (id,job_id,cmd,targets,is_single_cmd,job_started,job_completed, is_load_balanced)
                VALUES(NULL,:jobId,:cmd,:targets,:isSingleCommand,False,False,:isLoadBalanced)
            """

def INSERT_AGENT_JOB_COMMAND():
    return  """
                INSERT INTO agent_job(id,agent_id,job_id)
                VALUES(NULL,:agentId,:jobId)
            """

def INSERT_JOB_RESULT_COMMAND():
    return """
                INSERT INTO job_result (id,job_id,agent_id,job_result,start_time,finish_time,was_canceled)
                VALUES(NULL,:jobId,:agentId,NULL,:startTime,NULL,False)
            """

def INSERT_AGENT_COMMAND_COMMAND():
    return  """
                INSERT INTO agent_command (id, agent_id, command, command_started, command_finished)
                VALUES(NULL, :agentId, :command, :started, :finished)
            """
##############################################################################
########################## GET ROWS ##########################################

def GET_ALL_SCHEDULED_JOB_RESULT_INFO():
    return  """
                SELECT * FROM scheduled_job_results_mapping AS sjrm
                JOIN job_result AS jr
                ON sjrm.job_id == jr.job_id
                JOIN scheduled_job AS sj
                ON sj.id = sjrm.scheduled_job_id
                WHERE sj.workspace_id = :workspaceId
                order by job_run_date_time DESC;
            """
def GET_ALL_SCHEDULED_JOB_RESULTS_BY_SCHEDULED_JOB_ID():
    return  """
                SELECT * FROM scheduled_job_results_mapping AS sjrm
                JOIN job_result AS jr
                ON sjrm.job_id == jr.job_id
                JOIN scheduled_job AS sj
                ON sj.id = sjrm.scheduled_job_id
                WHERE sj.workspace_id = :workspaceId
                AND sj.id = :scheduledJobId
                order by job_run_date_time DESC;
            """


def GET_ALL_SCHEDULED_JOB_MAPPINGS_BY_ID_COMMAND():
    return  """ 
                SELECT * FROM scheduled_job_results_mapping 
                WHERE job_run_date_time >= datetime('now', '-24 hour') 
                AND scheduled_job_id = :scheduledJobId;
            """

def GET_ALL_UNRUN_JOBS_SCHEDULED_FOR_TODAY_COMMAND():
    return  """
                SELECT * FROM scheduled_job AS sj
                WHERE (strftime('%Y-%m-%d',sj.run_date_time) == strftime('%Y-%m-%d',datetime('now')) 
                OR sj.run_date_time == '') 
                AND sj.id 
                NOT IN
                    (SELECT scheduled_job_id FROM scheduled_job AS sj 
                    JOIN scheduled_job_results_mapping AS sjm
                    ON sj.id == sjm.scheduled_job_id
                    AND strftime('%Y-%m-%d',sjm.job_run_date_time) = strftime('%Y-%m-%d',datetime('now')));
            """

def GET_ALL_UNRUN_REOCCURING_DAILY_JOBS_COMMAND():
    return  """
                SELECT * FROM scheduled_job AS sj
                WHERE sj.run_type = 1 AND sj.id NOT IN
                    (SELECT scheduled_job_id FROM scheduled_job AS sj 
                    JOIN scheduled_job_results_mapping AS sjm
                    ON sj.id == sjm.scheduled_job_id
                    WHERE sj.run_type = 1
                    AND strftime('%Y-%m-%d',sjm.job_run_date_time) >= strftime('%Y-%m-%d',datetime('now')));
            """

def GET_ALL_REOCCURING_DAILY_JOBS_COMMAND():
    return  """
                SELECT * FROM scheduled_job
                WHERE run_type == 1;
            """

def GET_ALL_UNRUN_REOCCURING_WEEKLY_JOBS_COMMAND():
    return  """
                SELECT * FROM scheduled_job AS sj
                WHERE sj.run_type = 2 AND sj.id NOT IN
                    (SELECT scheduled_job_id FROM scheduled_job AS sj 
                    JOIN scheduled_job_results_mapping AS sjm
                    ON sj.id == sjm.scheduled_job_id
                    WHERE sj.run_type = 2
                    AND strftime('%Y-%m-%d',sjm.job_run_date_time) >= strftime('%Y-%m-%d',datetime('now', '-7 Day')));
            """

def GET_ALL_REOCCURING_WEEKLY_JOBS_COMMAND():
    return  """
                SELECT * FROM scheduled_job
                WHERE run_type == 2;
            """

def GET_ALL_UNRUN_REOCCURING_MONTHLY_JOBS_COMMAND():
    return  """
                SELECT * FROM scheduled_job AS sj
                WHERE sj.run_type = 3 AND sj.id NOT IN
                    (SELECT scheduled_job_id FROM scheduled_job AS sj 
                    JOIN scheduled_job_results_mapping AS sjm
                    ON sj.id == sjm.scheduled_job_id
                    WHERE sj.run_type = 3
                    AND strftime('%Y-%m-%d',sjm.job_run_date_time) >= strftime('%Y-%m-%d',datetime('now', '-30 Day')));
            """

def GET_ALL_REOCCURING_MONTHLY_JOBS_COMMAND():
    return  """
                SELECT * FROM scheduled_job
                WHERE run_type == 3;
            """

def GET_ALL_SCHEDULED_JOBS_COMMAND():
    return  """
                SELECT * FROM scheduled_job;
            """

def GET_ALL_SCHEDULED_JOBS_BY_WORKSPACE_ID_COMMAND():
    return  """
                SELECT * FROM scheduled_job WHERE workspace_id = :workspaceId;
            """

def GET_ALL_TARGET_COMMAND():
    return  """
                SELECT * FROM target;
            """

def GET_TARGET_BY_ID_COMMAND():
    return  """
                SELECT * FROM target WHERE id = :id
            """

def GET_TARGET_BY_TARGET_COMMAND():
    return  """
                SELECT * FROM target WHERE target = :target COLLATE NOCASE
            """

def GET_ALL_TARGET_JOB():
    return  """
                SELECT * FROM target_job
            """

def GET_TARGET_JOBS_BY_TARGET_ID():
    return  """
                SELECT * FROM target_job WHERE target_id = :targetId
            """

def GET_ALL_STREAM_EVENTS_COMMAND():
    return  """
                SELECT * FROM stream_event ORDER BY report_time DESC;
            """

def GET_ALL_COMMAND_TEMPLATE_COMMAND():
    return  """
                SELECT * FROM command_template;
            """

def GET_ALL_WORKSPACES():
    return  """
                SELECT * FROM workspace;
            """

def GET_ALL_MESSAGES_COMMAND():
    return  """
                SELECT * FROM message;
            """

def GET_ALL_JOBS_COMMAND():
    return  """
                SELECT * FROM job;
            """

def GET_ALL_JOBS_BY_WORKSPACE_ID_COMMAND():
    return  """
                SELECT * FROM job AS j
                JOIN workspace_job AS wj
                ON j.job_id = wj.job_id
                WHERE wj.workspace_id = :workspaceId
                ORDER BY id DESC;
            """

def GET_ALL_NEW_JOBS_COMMAND():
    return  """
                SELECT * FROM job WHERE job_started = 0
            """

def GET_AGENT_COUNT_COMMAND():
    return  """
                SELECT COUNT(*) FROM agent
            """

def GET_ACTIVE_AGENT_COUNT_COMMAND():
    return  """
                SELECT COUNT(*) FROM agent WHERE is_active = 1
            """

def GET_ALL_AGENTS():
    return  """
                SELECT * FROM agent
            """

def GET_ALL_ACTIVE_AGENTS():
    return  """
                SELECT * FROM agent WHERE is_active = 1
            """


def GET_ALL_AGENTS_AND_HEALTH_RECORDS():
    return  """
                SELECT * FROM agent AS a LEFT JOIN agent_health AS ah WHERE a.id == ah.agent_id
            """

def GET_AGENT_BY_IP():
    return  """
                SELECT * FROM agent WHERE ip_address = :agentIp
            """

def GET_AGENT_BY_ID():
    return  """
                SELECT * FROM agent WHERE id = :agentId
            """

def GET_AGENT_AND_HEALTH_RECORD_BY_ID():
     return  """
                SELECT * FROM agent AS a LEFT JOIN agent_health AS ah WHERE a.id == :agentId AND a.id == ah.agent_id;
            """
def GET_AGENT_JOBS_BY_DAY():
    return  """
                SELECT COUNT(finish_time), date(finish_time)
                FROM job_result
                WHERE agent_id = :agentId
                AND date('now','localtime')
                GROUP BY date(finish_time);
            """

def GET_AGENT_JOBS():
    return  """
                SELECT * FROM agent_job;
            """

def GET_ALL_RUNNING_JOBS():
    return """
                SELECT _agent.ip_address, _result.job_id, _agent.id
                FROM job_result as _result
                LEFT JOIN agent AS _agent ON _agent.id = _result.agent_id
                WHERE finish_time IS NULL AND job_result IS NULL;
            """

def GET_USER_BY_USERNAME_COMMAND():
    return  """
                SELECT * FROM user WHERE username = :uname
            """

def GET_ADMIN_USER_COUNT_COMMAND():
    return  """
                SELECT COUNT(*) FROM user WHERE username = 'admin'
            """

def GET_JOB_COUNT_COMMAND():
    return  """
                SELECT COUNT(*) FROM job AS j
                JOIN workspace_job AS wj
                ON j.job_id = wj.job_id 
                JOIN job_result AS jr 
                ON wj.job_id = jr.job_id
                WHERE wj.workspace_id = :workspaceId 
                AND job_started = 1 
                AND jr.finish_time IS NULL;
            """

def GET_JOB_BY_ID_COMMAND():
    return f"""
                SELECT * FROM job WHERE job_id = :jobId
            """

def GET_JOB_COUNT_BY_ID_COMMAND():
    return  f"""
                SELECT COUNT(*)
                FROM agent_job
                WHERE agent_id = :jobId
            """

def GET_ACTIVE_JOB_COUNT_BY_ID_COMMAND():
    return  f"""
                SELECT COUNT(*)
                FROM job_result
                WHERE agent_id = :agentId
                AND finish_time IS NULL;
            """

def GET_COMPLETED_JOB_COUNT_COMMAND():
    return  """
                SELECT COUNT(*) FROM job AS j
                JOIN workspace_job AS wj
                ON j.job_id = wj.job_id
                WHERE wj.workspace_id = :workspaceId
                AND job_completed = 1
                AND job_started = 1
            """
def GET_PENDING_JOB_COUNT_COMMAND():
    return  """
                SELECT COUNT(*) FROM job AS j
                JOIN workspace_job AS wj
                ON j.job_id = wj.job_id
                WHERE wj.workspace_id = :workspaceId
                AND job_completed = 0
                AND job_started = 0
            """

def GET_JOB_RESULT_BY_ID_COMMAND():
    return  """
               select jr.id, jr.job_id, jr.agent_id, jr.job_result, jr.start_time, jr.finish_time, jr.was_canceled, j.cmd, a.ip_address from job_result as jr join job as j on j.job_id == jr.job_id join agent as a on a.id = jr.agent_id WHERE jr.job_id = :jobid
            """

def GET_ALL_AGENT_COMMANDS():
    return  """
                SELECT * FROM agent_command WHERE command_started == False
            """
##############################################################################
########################## UPDATE ROWS #######################################
def UPDATE_USER_PASSWORD_BY_USERNAME():
    return  """
                UPDATE user
                SET passwordhash = :passhash
                WHERE username = :uname
            """

def UPDATE_SCHEDULED_JOB_MAPPING_RUN_TIME():
    return  """
                UPDATE scheduled_job_results_mapping
                SET job_run_date_time = :jobRunTime
                WHERE job_id = :jobId;
            """

def UPDATE_JOB_STARTED_COMMAND():
    return  """
                UPDATE job
                SET job_started = True
                WHERE job_id = :jobId
            """

def UPDATE_JOB_RESET_JOB_STATUS_COMMAND():
    return  """
                UPDATE job
                SET job_started = False
                WHERE job_id = :jobId
            """

def UPDATE_JOB_FINISHED_COMMAND():
    return  """
                UPDATE job
                SET job_completed = True
                WHERE job_id = :jobId
            """

def UPDATE_JOB_FINISHED_BY_AGENT_ID_COMMAND():
    return  """
                UPDATE job
                SET job_completed = True
                WHERE job_id = :agentId
            """

def UPDATE_JOB_RESULT_COMMAND():
    return """
                UPDATE job_result
                SET
                    job_result = :result,
                    finish_time = :finishTime,
                    was_canceled = :wasCanceled
                WHERE
                    job_id = :jobId
                    and agent_id = :agentId
            """

def UPSERT_AGENT_HEALTH_REPORT_COMMAND():
    return """
                INSERT INTO agent_health(id,agent_id,memory_percent,storage_percent,cpu_percent,report_time,log_size,running_processes)
                VALUES(NULL,:agentId,:memPct,:stgPct,:cpuPct,:reportTime,:logSize,:runningProcesses)
                ON CONFLICT(agent_id) DO UPDATE SET
                    memory_percent = :memPct,
                    storage_percent = :stgPct,
                    cpu_percent = :cpuPct,
                    report_time = :reportTime,
                    log_size = :logSize,
                    running_processes = :runningProcesses
                WHERE agent_id = :agentId
            """

def UPDATE_AGENT_COMMANDS_COMMAND():
    return  """
                UPDATE agent_command SET command_started = 1, command_finished = 1 WHERE id = :agentId
            """

def SET_AGENT_INACTIVE_COMMAND():
    return  """
                UPDATE agent SET is_active = 0 WHERE id = :agentId
            """

def SET_AGENT_ACTIVE_COMMAND():
    return  """
                UPDATE agent SET is_active = 1 WHERE ip_address = :agentIp
            """

def IGNORE_TARGET_BY_TARGET_COMMAND():
    return  """
                UPDATE target SET ignore = True WHERE target = :target COLLATE NOCASE
            """

def BATCH_IGNORE_TARGET_BY_TARGETS_COMMAND():
    return  """UPDATE target SET ignore = True WHERE target in"""
    
##############################################################################
########################## DELETE ROWS #######################################

def DELETE_COMMAND_TEMPLATE_COMMAND():
    return  """
                DELETE FROM command_template WHERE id = :id;
            """

def REMOVE_SCHEDULED_JOB_COMMAND():
    return  """
                DELETE FROM scheduled_job WHERE id = :scheduledJobId;
            """

def CLEAR_ALL_COMPLETED_JOBS_COMMAND():
    return  """
                DELETE FROM job WHERE job_completed = 1;
            """

def CLEAR_ALL_COMPLETED_JOB_RESULTS_COMMAND():
    return  """
                DELETE FROM job_result WHERE finish_time IS NOT NULL;
            """

def CLEAR_MESSAGE_BY_ID_COMMAND():
    return  """
                DELETE FROM message WHERE id = :messageId;
            """

def CLEAR_ALL_MESSAGES_COMMAND():
    return  """
                DELETE FROM message;
            """

def TRIM_STREAM_EVENT_TABLE_COMMAND():
    return  """
                DELETE FROM stream_event WHERE id NOT IN (SELECT id FROM stream_event ORDER BY report_time DESC LIMIT 100)
            """

def REMOVE_TARGET_BY_TARGET_COMMAND():
    return  """
                DELETE FROM target WHERE target = :target COLLATE NOCASE;
            """