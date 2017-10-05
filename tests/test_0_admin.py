# -*- coding: UTF-8 -*-
import utils

from utils import Settings, login

def test_admin_respond_200():
    assert utils.is_status_ok(utils.call('GET', url='/status/is_up').status_code)


def test_admin_login():
    res = utils.call('POST', url='/b/login', json=Settings.ADMIN)
    assert utils.is_status_ok(res.status_code)

    res = res.json()

    assert res['login']
    assert len(res['token']) > 32


def test_admin_is_on_status(login):
    res = utils.call('GET',
                        url='/b/admin/is_on',
                        json={'username': 'frontageadmin', 'password': 'frontagepassword'},
                        headers={'Authorization': 'Bearer '+login})
    assert utils.is_status_ok(res.status_code)

    res = res.json()
    assert isinstance(res['on'], bool)


