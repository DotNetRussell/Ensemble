FROM alpine:latest

# Uncomment to workaround behind any corp proxy:
RUN sed -ie "s/https/http/g" /etc/apk/repositories

RUN apk add --no-cache ca-certificates
RUN update-ca-certificates

# May be need to be explicitly trusted depending on corporate proxy.
ARG TRUSTED_PYPI_HOSTS="--trusted-host pypi.org --trusted-host pypi.python.org --trusted-host=files.pythonhosted.org"

RUN apk update && \
        apk upgrade --available && \
        apk add --no-cache \
        openssl \
        py3-pip \
        python3-dev \
        gcc \
        musl-dev \
        linux-headers

# gcc, musl-dev, linux-headers are needed for psutil package in requirements.txt.


# Uncomment if workaround was used:
RUN sed -ie "s/http/https/g" /etc/apk/repositories

# Ensure our working directory is in path command executions are off '.'.
ENV PATH="${PATH}:/home/site/wwroot"

COPY . /home/site/wwwroot
WORKDIR /home/site/wwwroot

COPY requirements.txt .
COPY /common/communication.py .
COPY /common/database_access.py .
COPY /common/encryption.py .
COPY /common/ensemble_constants.py .
COPY /common/ensemble_enums.py .
COPY /common/ensemble_logging.py .

# We expect this to be created already.  Explicit copy to error if missing.
COPY /server/.config.json .

RUN pip3 install ${TRUSTED_PYPI_HOSTS} -r requirements.txt

ADD ./* .

RUN chmod +x ensemble_director.py

RUN pip --no-cache-dir install -r requirements.txt
CMD ["python3", "ensemble_director.py"]