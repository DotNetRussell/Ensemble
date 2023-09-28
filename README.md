<p align="center">
  <image src="/static/images/ensemble.png"/>
</p>

# Ensemble
A Bug Bounty Platform that allows hunters to issue commands over a geo-distributed cluster. The ideal user is someone who is attempting to scan multiple bug bounty programs simultaneously, on a recurring basis

## Usage

For every Ensemble cluster to function you will need to have at least one director and one agent.

---

### Installing Ensemble

Ensemble is a cluster of machines. So at a minimum you're going to want at least two. One machine to be the director and web portal that you access and another machine that is a node in your cluster. Ideally though you would have a node for every region in the world. I used Digital Ocean for setting up a global cluster but you can use any VPS provider you'd like. 


This is the least amount of commands to run to start an ensemble server. The server doesn't require any extra tooling as all commands are run on the agents. Your server can and should be very light weight.


```
apt-get update
apt install git -y;
apt install python3
apt install pipx
git clone https://github.com/DotNetRussell/Ensemble.git;
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

*NOTE* Some users have experienced an issue where flask is installed but when you run ensemble it says it's not installed. I that happens just use the command below. 

`apt install python3-flask`

---

### Starting an Ensemble Director Server

Ensemble Director is the master node of your cluster. It will not only be the web portal that you connect to and control your cluster with but it will also be the node that all other nodes in the cluster communicate with.

To start a director once fully installed, run the following command
`./server/ensemble_director.py --config-file <see-sample-config>` 

Next, visit the IP of your director on port 5000 and create your admin account. 
_DO THIS IMMEDIATELY AFTER STARTING THE DIRECTOR_  
`https://127.0.0.1:5000`

*NOTE* You will need to use `https` protocol. It will say it's an insecure connection because the ensemble_director just generated a new unique certificate for you and it's not registered with a certificate authority.  

---

### Creating an Ensemble Agent

Creating an ensemble agent is relatively easy. The director has generated a new symmetric key for you and the command you need to run your agent. Just visit your Ensemble Director settings page and you will find the command you need to run.

```sh
apt-get update;
apt install git -y;
apt install python3;
apt install python3-psutil;
git clone https://github.com/DotNetRussell/Ensemble.git;
cd Ensemble;

pip install -r requirements.txt

./client/ensemble_agent.py --connection-string '{"HOST":"<your_server_ip>","PORT":"5680","ENCRYPTION_KEY":"<your_symmetric_key>"}'
```


*NOTE* As soon as your agent is running, it will appear on your director web portal. 

--- 

### Docker

All commands should be run from the root of the repository.
Build the client image:
```sh
docker build -f ./client/Dockerfile --build-arg ENCRYPTION_KEY=your_key --build-arg HOST=your_server_ip --build-arg PORT=5680 -t ensemble_client:latest . 
```

Build the server image.  It's expected that you have created a `config.json` file similar to the Sample-Config.json
for your configuration in the `server` directory.  The server image build expects this:
```sh
docker build -f ./server/Dockerfile -t ensemble_server:latest .
```

Docker compose to create containers from images:
```sh
docker compose up
```
Docker tear down:
```sh
docker compose down
```


#### Debug
Run interactive shell session for client:
```sh
docker run --rm -it --entrypoint bash ensemble_client
```

Run interactive shell session for server:
```sh
docker run --rm -it --entrypoint /bin/sh ensemble_server
```


#### Cleanup
```sh
docker image rmi ensemble_client
docker image rmi ensemble_server
docker system prune
```


### Navigating the Application

#### Dashboard Page
![Alt text](https://i.imgur.com/eCPupxf.png)

- The Dashboard is where you can easily see where your active agents are distributed in the world.
- It also displays statistics about the jobs that are running and that have completed.
- This is also where you create and switch workspaces. This is helpful for separating out bug bounties 


#### Agents Page
![Alt text](https://i.imgur.com/tLgVn75.png)

- The agents page shows you statistics about your agents. This includes their health, if they're active or offline, and how many jobs they're running.

#### Agent Health Page
![Alt text](https://i.imgur.com/dZMy9mx.png)

- The agent health page shows you detailed information about each agent.
- This includes memory consumption, remaining storage, CPU usage, log file size, job history and running processes
- You also have some control over the agent on this page

#### Jobs Page
![Alt text](https://i.imgur.com/Cw9DBER.png)

- The jobs page shows you running and completed jobs as well as details about the jobs.
- Clicking the magnified glass will navigate to the Job Results page which is an aggregation of all of the job output from all agents
  
#### Job Results Page
![Alt text](https://i.imgur.com/ktV4Hmo.png)

- The job results page shows detailed information about the job results from each agent the job ran on

#### Scheduled Jobs Page
![Alt text](https://i.imgur.com/Wa5Nhrb.png)

- The scheduled jobs page shows you the jobs that have been scheduled to run.
- Jobs that run on recurring schedule daily/weekly/monthly, will appear under the completed scheduled jobs section and you'll be able to diff the results between runs. This is nice for finding changes in a attack surface over time.

#### Create New Job Page
![Alt text](https://i.imgur.com/XE8edSy.png)

- Create new job page allows users to create new jobs to run instantly, run on a recurring basis, or schedule the job to run at a specific date and time
- Running a load balanced command is best used when you expect the results will be the same regardless what region you run the command in. This will take your command and distribute it across the cluster evenly based on how many targets you have. For example, if you have 4 nodes, and only one target defined, it will issue the job only to the first node. If you have 4 nodes and two targets defined, then it'll issue one target to the first node and one target to the second node.
- Not running a command with the load balanced flag on means that your command and all targets will be issued to every node equally. For example, if you have 4 nodes, and one target. Then each node will run the same command against that one target.
- Run as a single command will run identical to what is described previously except that it will dump all targets into a temporary file, then put the file into the command where you defined {{target}}
- Templates have been added to the application by default but you can run whatever commands you'd like in the command input. You can also create your own templates for future use. 

#### Event Stream Page
![Alt text](https://i.imgur.com/eQKJDHD.png)

- Displays the last 100 events to have taken place on the server

#### Settings Page
![Alt text](https://i.imgur.com/jaCAAD2.png)

- Lets users update their password as well as add and remove command templates
- This is also where you will be able to retrieve the command to run your agent
