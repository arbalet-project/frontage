FROM python:latest
RUN apt-get update && apt-get install -y python3-dev netcat
RUN mkdir -p /usr/src/app
COPY ./arbalet/frontage/requirements.txt /usr/src/app/requirements.txt
RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt

COPY docker-entrypoint.sh /
COPY wait-for-it.sh /
COPY ./arbalet/frontage/ /usr/src/app/

WORKDIR /usr/src/app

ENTRYPOINT ["/docker-entrypoint.sh"]
