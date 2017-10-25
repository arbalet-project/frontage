# -*- coding: UTF-8 -*-
import json
import datetime
import requests
import pytest

class Settings(object):
    BASE_URL = "http://127.0.0.1:8123"
    ADMIN = {'username': 'frontageadmin', 'password': 'frontagepassword'}
    USER = {'username': '__XXX__'}


def call(method, url, headers=None, **kwargs):
    req_headers = dict()
    if headers:
        req_headers.update(headers)
    return requests.request(method=method, url=Settings.BASE_URL + url, headers=req_headers, **kwargs)

def is_status_ok(status):
    return 200 <= status < 300

def is_iso_date(date):
    try:
        if date:
            datetime.datetime.strptime(date, '%Y-%m-%d')
        return True
    except ValueError:
        pass
    return False


@pytest.fixture
def login():
    return call('POST', url='/b/login', json=Settings.ADMIN).json()['token']