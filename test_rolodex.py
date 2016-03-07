# -*- coding: utf-8 -*-
# pylint: disable-msg=C0103, line-too-long

"""
    Rolodex Tests
"""

import json
import pytest
import rolodex

@pytest.fixture
def client(request):
    client = rolodex.app.test_client()
    return client

def dbg(method, uri, rv):
    """ personal sanity; use with py.test -s flag """
    print "================="
    print "REQ> ", method, uri, rv.status_code
    print rv.headers
    print "RAW>", rv.data

"""
Group tests
 - the update (PUT) test occurs later in sequence with user
"""

def test_post_group(client):
    """ add new group"""
    group_name = 'clowns'
    uri = "/groups"
    req = {
        "name": group_name
    }
    rv = client.post(uri,
                     data=json.dumps(req),
                     headers=[('Content-type', 'application/json')])
    dbg('POST', uri, rv)
    assert rv.status_code == 201


def test_get_group(client):
    """ add new group"""
    group_name = 'clowns'
    uri = "/groups/" + group_name
    req = {
        "name": group_name
    }
    rv = client.get(uri)
    dbg('GET', uri, rv)
    assert rv.status_code == 200
    res = json.loads(rv.data)
    assert res["group_name"] == group_name
    assert len(res["users"]) == 0

def test_delete_group(client):
    group_name = 'clowns'
    uri = "/groups/" + group_name
    rv = client.delete(uri)
    dbg('DELETE', uri, rv)
    assert rv.status_code == 200


def test_nonexistent_group(client):
    """ handle non-existent group """
    group_name = 'clowns'
    uri = '/groups/' + group_name
    rv = client.get(uri)
    dbg('GET', uri, rv)
    assert rv.status_code == 404

    rv = client.delete(uri)
    dbg('DELETE', uri, rv)
    assert rv.status_code == 404


"""
user routes testing 
  - this involves a bit more group testing in sequence
"""
def test_post_user(client):
    """ add new user """
    userid = 'jim'
    uri = '/users'
    req = {
        "userid": userid,
        "first_name": "Jim",
        "last_name": "Jones",
        "groups": ["admin"]
    }
    rv = client.post(uri,
                     data=json.dumps(req),
                     headers=[('Content-type', 'application/json')])
    dbg('POST', uri, rv)
    assert rv.status_code == 201
    res = json.loads(rv.data)
    assert isinstance(res, dict)
    assert res["userid"] == userid
    assert len(res["groups"]) == 1

def test_put_user(client):
    """ update user"""
    userid = 'jim'
    uri = '/users/' + userid
    req = {
        "userid": userid,
        "first_name": "Reverend Jim",
        "last_name": "Jones",
        "groups": ["admin", "jonestown"]

    }
    rv = client.put(uri,
                    data=json.dumps(req),
                    headers=[('Content-type', 'application/json')])
    dbg('PUT', uri, rv)
    assert rv.status_code == 200
    res = json.loads(rv.data)
    assert "userid" in rv.data
    assert isinstance(res, dict)
    assert len(res["groups"]) == 2


def test_get_user(client):
    """ get modified user"""
    userid = 'jim'
    uri = '/users/' + userid
    rv = client.get(uri)
    dbg('GET', uri, rv)
    assert rv.status_code == 200
    res = json.loads(rv.data)
    assert len(res["groups"]) == 2


def test_get_user_groups(client):
    """ get the new group """
    group_name = 'jonestown'
    uri = '/groups/' + group_name
    rv = client.get(uri)
    dbg('GET', uri, rv)
    assert rv.status_code == 200
    res = json.loads(rv.data)
    assert len(res["users"]) == 1
    assert res["users"][0] == "jim"

def test_delete_user_group(client):
    """ get the new group """
    group_name = 'jonestown'
    uri = '/groups/' + group_name
    rv = client.delete(uri)
    dbg('DELETE', uri, rv)
    assert rv.status_code == 200

    rv = client.get(uri)
    dbg('GET', uri, rv)
    assert rv.status_code == 404

def test_delete_user(client):
    """ delete the user"""
    userid = 'jim'
    uri = '/users/' + userid
    rv = client.delete(uri)
    dbg('DELETE', uri, rv)
    assert rv.status_code == 200

def test_nonexistent_user(client):
    """ handle non-existent user """
    userid = 'jim'
    uri = '/users/' + userid
    rv = client.get(uri)
    dbg('GET', uri, rv)
    assert rv.status_code == 404

    rv = client.delete(uri)
    dbg('DELETE', uri, rv)
    assert rv.status_code == 404

