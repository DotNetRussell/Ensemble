FROM alpine:latest

RUN apk update
RUN apk add py-pip
RUN apk add --no-cache python3-dev 
RUN pip install --upgrade pip


COPY . /home/site/wwwroot
WORKDIR /home/site/wwwroot


RUN pip --no-cache-dir install -r requirements.txt
CMD ["python3", "app.py"]