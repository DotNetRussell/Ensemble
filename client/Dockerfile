FROM kalilinux/kali-last-release

# Install packages
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    apt-transport-https \
    #kali-linux-headless \
    python3 \
    python3-pip \
    procps


# May be need to be explicitly trusted depending on corporate proxy.
ARG TRUSTED_PYPI_HOSTS="--trusted-host pypi.org --trusted-host pypi.python.org --trusted-host=files.pythonhosted.org"

WORKDIR /root

CMD mkdir Ensemble

WORKDIR /root/Ensemble

COPY requirements.txt .
COPY /common/communication.py .
COPY /common/encryption.py .
COPY /common/ensemble_constants.py .
COPY /common/ensemble_logging.py .

COPY /client/ensemble_agent.py .
RUN chmod +x ensemble_agent.py
#RUN ["chmod", "+x", "/root/Ensemble/ensemble_agent.py"]


RUN pip3 install ${TRUSTED_PYPI_HOSTS} -r requirements.txt
# RUN python3 -m pip install ${TRUSTED_PYPI_HOSTS} --upgrade pip \
#     && pip install ${TRUSTED_PYPI_HOSTS} -r requirements.txt


# Must pass in the ENCRYPTION_KEY via build-arg (--build-arg ENCRYPTION_KEY=your_key --build-arg HOST=your_host --build-arg PORT=your_port)
ARG ENCRYPTION_KEY HOST PORT
ENV ENCRYPTION_KEY=$ENCRYPTION_KEY HOST=$HOST PORT=$PORT


# For Debugging.
#RUN echo "{\"ENCRYPTION_KEY\":\"$ENCRYPTION_KEY\", \"HOST\": \"$HOST\", \"PORT\":\"$PORT\"}"
#ENTRYPOINT echo "{\"ENCRYPTION_KEY\":\"$ENCRYPTION_KEY\", \"HOST\": \"$HOST\", \"PORT\":\"$PORT\"}"

# Can split to separate arguments instead of connection string.
ENTRYPOINT python3 ensemble_agent.py --connection-string "{\"ENCRYPTION_KEY\":\"$ENCRYPTION_KEY\", \"HOST\": \"$HOST\", \"PORT\":\"$PORT\"}"

