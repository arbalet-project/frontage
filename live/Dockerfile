FROM node:8
RUN mkdir /home/node/live
COPY ./ /home/node/live/
RUN rm /home/node/live/public/config.json
RUN cd /home/node/live && npm install

ENTRYPOINT ["node", "/home/node/live/main.js"]
