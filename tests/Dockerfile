FROM python:2

RUN mkdir -p /usr/src/app

COPY requirements.txt /usr/src/app/
WORKDIR /usr/src/app

RUN pip install -r requirements.txt

COPY . /usr/src/app/

CMD py.test --exitfirst --capture=no  -vv --showlocals --failed-firs --color=yes