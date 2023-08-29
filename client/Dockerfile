FROM kalilinux/kali-last-release

# Install packages
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    apt-transport-https \
    kali-linux-headless \
    python3 \
    python3-pip \
    procps


WORKDIR /root

CMD mkdir Ensemble

WORKDIR /root/Ensemble

COPY ../requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ensemble_agent.py ensemble_agent.py
RUN chmod +x ensemble_agent.py

#RUN ["chmod", "+x", "/root/Ensemble/ensemble_agent.py"]


COPY common/communication.py communication.py
COPY common/encryption.py encryption.py
COPY common/ensemble_logging.py ensemble_logging.py
COPY common/ensemble_constants.py ensemble_constants.py


# Must pass in the ENSEMBLE_ENCRYPTION_KEY via build-arg (--build-arg ENSEMBLE_ENCRYPTION_KEY=your_key)
ARG ENSEMBLE_ENCRYPTION_KEY HOST PORT
ENV ENSEMBLE_ENCRYPTION_KEY=$ENSEMBLE_ENCRYPTION_KEY HOST=$HOST PORT=$PORT


RUN echo '{"ENCRYPTION_KEY":"${ENSEMBLE_ENCRYPTION_KEY}", "HOST":"${HOST}", "PORT":"${PORT}"}'

#RUN /root/Ensemble/ensemble_agent.py --connection-string '{"ENCRYPTION_KEY":"${ENSEMBLE_ENCRYPTION_KEY}", "HOST":"${HOST}", "PORT":"${PORT}"}'

