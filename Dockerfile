FROM python:latest
RUN mkdir -p /usr/src/app
COPY ./arbalet/frontage/ /usr/src/app/
COPY docker-entrypoint.sh /
COPY wait-for-it.sh /

WORKDIR /usr/src/app


RUN apt-get update && apt-get install -y python3-dev netcat
RUN pip install --no-cache-dir -r requirements.txt


ENTRYPOINT ["/docker-entrypoint.sh"]
