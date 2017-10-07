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
                        headers={'Authorization': 'Bearer '+login})
    assert utils.is_status_ok(res.status_code)

    res = res.json()
    assert isinstance(res['on'], bool)


def test_admin_set_enabled_true(login):
    res = utils.call('POST',
                        url='/b/admin/enabled',
                        json={'enabled': True},
                        headers={'Authorization': 'Bearer '+login})
    assert utils.is_status_ok(res.status_code)
    res = res.json()
    assert res['enabled'] == True

def test_admin_set_enabled_false(login):
    res = utils.call('POST',
                        url='/b/admin/enabled',
                        json={'enabled': False},
                        headers={'Authorization': 'Bearer '+login})
    assert utils.is_status_ok(res.status_code)
    res = res.json()
    assert res['enabled'] == False


def test_admin_cal(login):
    res = utils.call('GET',
                        url='/b/admin/cal',
                        headers={'Authorization': 'Bearer '+login})
    assert utils.is_status_ok(res.status_code)

    res = res.json()
    print(res)
    assert isinstance(res['on'], (str, unicode))
    assert isinstance(res['off'], (str, unicode))


def test_admin_cal_at(login):
    res = utils.call('GET',
                        url='/b/admin/cal/2017-10-07',
                        headers={'Authorization': 'Bearer '+login})
    assert utils.is_status_ok(res.status_code)

    res = res.json()
    print(res)
    assert isinstance(res['on'], (str, unicode))
    assert isinstance(res['off'], (str, unicode))
    assert res['on'] == '19:08'
    assert res['off'] == '04:31'


def test_admin_set_cal_at(login):
    on_at = '22:22'
    off_at = '01:22'
    res = utils.call('PATCH',
                        url='/b/admin/cal/2017-10-07',
                        json={'on': on_at, 'off': off_at},
                        headers={'Authorization': 'Bearer '+login})
    assert utils.is_status_ok(res.status_code)

    res = res.json()
    assert isinstance(res['on'], (str, unicode))
    assert isinstance(res['off'], (str, unicode))
    assert res['on'] == on_at
    assert res['off'] == off_at

    res = utils.call('PATCH',
                        url='/b/admin/cal/2017-10-07',
                        json={'on': '19:08', 'off': '04:31'},
                        headers={'Authorization': 'Bearer '+login})
    assert utils.is_status_ok(res.status_code)


def test_admin_apps_list(login):
    res = utils.call('GET',
                        url='/b/admin/apps',
                        headers={'Authorization': 'Bearer '+login})
    assert utils.is_status_ok(res.status_code)

    res = res.json()
    assert isinstance(res, dict)


def test_admin_current_app(login):
    res = utils.call('GET',
                        url='/b/admin/apps/running',
                        headers={'Authorization': 'Bearer '+login})
    assert utils.is_status_ok(res.status_code)
    res = res.json()
    assert isinstance(res, dict)
    if res:
        assert 'name' in res
        assert res['started_at']
        assert 'params' in res
        assert 'username' in res

def test_admin_current_app_set(login):
    res = utils.call('POST',
                        url='/b/admin/apps/running',
                        json={'name': 'flag', 'params': ''},
                        headers={'Authorization': 'Bearer '+login})
    assert utils.is_status_ok(res.status_code)







