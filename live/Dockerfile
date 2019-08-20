FROM node:8
RUN mkdir /home/node/live
COPY ./ /home/node/live/
RUN cd /home/node/live && npm install

ENTRYPOINT ["node", "/home/node/live/main.js"]
