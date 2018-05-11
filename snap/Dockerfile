FROM nginx:latest
RUN apt-get update && apt-get install -y git
RUN if [ ! -d /usr/src/Snap--Build-Your-Own-Blocks ]; then git clone -q https://github.com/jmoenig/Snap--Build-Your-Own-Blocks.git /usr/src/Snap--Build-Your-Own-Blocks; fi
RUN rm -rf /usr/share/nginx/html
RUN ln -snf /usr/src/Snap--Build-Your-Own-Blocks /usr/share/nginx/html
COPY ./arbalet-frontage.xml /usr/src/Snap--Build-Your-Own-Blocks/
COPY ./index.html /usr/src/Snap--Build-Your-Own-Blocks/
