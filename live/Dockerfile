FROM node:8
RUN mkdir /home/node/live
COPY wait-for-it.sh /
COPY ./ /home/node/live/
RUN rm /home/node/live/public/config.json
RUN cd /home/node/live && npm install
WORKDIR /home/node/live
ENTRYPOINT ["/home/node/live/docker-entrypoint.sh"]
