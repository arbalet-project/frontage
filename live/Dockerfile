FROM node:8
RUN mkdir /home/node/live
COPY ./ /home/node/live/
RUN chmod 777 /home/node/live/public/config.json
RUN cd /home/node/live && npm install

ENTRYPOINT ["node", "/home/node/live/main.js"]
