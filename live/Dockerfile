FROM node:12
COPY wait-for-it.sh /
RUN mkdir -p /home/node/live
COPY . /home/node/live/
WORKDIR /home/node/live
RUN cd /home/node/live && npm i --verbose
RUN rm /home/node/live/public/config.json
ENTRYPOINT ["/home/node/live/docker-entrypoint.sh"]
