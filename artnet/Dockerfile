FROM python:3.6

RUN mkdir -p /usr/src/app
COPY wait-for-it.sh /
COPY . /usr/src/app/
RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt

ENV TZ=Europe/Paris
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /usr/src/app

ENTRYPOINT ["/usr/src/app/docker-entrypoint.sh"]
