FROM kalilinux/kali-last-release

RUN apt-get update && apt-get upgrade -y && apt-get install -y  apt-transport-https
RUN apt-get install python3 -y && apt-get install python3-pip -y && apt-get install procps -y;

WORKDIR /root/

CMD mkdir Ensemble

WORKDIR /root/Ensemble

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ensemble_agent ensemble_agent
RUN chmod +x ensemble_agent
COPY communication.py communication.py
COPY encryption.py encryption.py
COPY ensemble_logging.py ensemble_logging.py
COPY ensemble_constants.py ensemble_constants.py

RUN /root/Ensemble/ensemble_agent --connection-string '{"ENCRYPTION_KEY":"", "HOST":"", "PORT":""}'

