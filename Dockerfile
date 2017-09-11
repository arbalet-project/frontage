FROM python:2.7
RUN mkdir -p /usr/src/app
COPY ./arbalet/frontage/ /usr/src/app/
COPY docker-entrypoint.sh /

WORKDIR /usr/src/app
RUN apt-get update && apt-get install -y python2.7-dev
RUN pip install --no-cache-dir -r requirements.txt


ENTRYPOINT ["/docker-entrypoint.sh"]
