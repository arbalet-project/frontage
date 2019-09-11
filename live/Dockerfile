FROM node:8
RUN mkdir /home/node/live
COPY wait-for-it.sh /
RUN cd /home/node/live && npm i
WORKDIR /home/node/live
ENTRYPOINT ["/home/node/live/docker-entrypoint.sh"]
