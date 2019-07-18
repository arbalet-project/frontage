FROM node:8
ONBUILD RUN mkdir /home/node/live && cp -R ./* /home/node/live
ONBUILD RUN cd /home/node/live && npm install
