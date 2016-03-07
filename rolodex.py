# -*- coding: utf-8 -*-
# pylint: disable-msg=C0103, line-too-long

"""
CRUD API for rolodex
"""

import json
import psycopg2
from flask import Flask, request, abort, jsonify

DEBUG = True

app = Flask(__name__)
app.Debug = DEBUG

db_conn = psycopg2.connect(
    host="localhost",
    port="5432",
    user="planet",
    password="planet",
    database="postgres",
    )


def pg_array_string(key, r):
    """ PG helper create suitable ARRAY[] string """
    default_str = "ARRAY[]::varchar[]"
    if not key in r:
        return default_str
    elif not isinstance(r[key], list):
        return default_str
    elif len(r[key]) == 0:
        return default_str

    return 'ARRAY[' +  ','.join(["'%s'" % e for e in r[key]]) + ']'



@app.route('/users', methods=['GET'])
def get_all_users():
    """ GET /users/<userid> """

    cur = db_conn.cursor()
    cur.execute("SELECT row_to_json(r) FROM user_view r")
    e = cur.fetchall()
    if not e or not e[0]:
        return jsonify([]), 200

    cur.close()
    res = json.dumps([r[0] for r in e], indent=2)
    return res, 200, {'Content-Type':'application/json'}


@app.route('/users', methods=['POST'])
def user_add():
    """ POST /users """
    req = request.get_json(silent=True)
    res = {}

    if not req or not "userid" in req:
        return jsonify(res), 400

    userid = req["userid"]

    cur = db_conn.cursor()
    cur.execute("SELECT user_exists(%s)", (userid,))
    e = cur.fetchone()
    if e[0] is True:
        return jsonify(res), 409

    array_str = pg_array_string('groups', req)

    try:
        cur.execute(
            "SELECT * FROM user_add(%(userid)s, %(first_name)s, %(last_name)s, " + array_str + ")",
            req)
    except Exception, e:
        print "FAIL", e
        cur.close()
        db_conn.rollback()
        return jsonify(res), 400

    e = cur.fetchone()
    db_conn.commit()
    cur.close()
    res_json = json.dumps(e[0], indent=2)
    return res_json, 201, {'Content-Type':'application/json'}



@app.route('/users/<userid>', methods=['GET'])
def user_get(userid):
    """ GET /users/<userid> """

    res = {}
    cur = db_conn.cursor()
    cur.execute("SELECT user_exists(%s)", (userid,))
    e = cur.fetchone()
    if e[0] is False:
        return jsonify(res), 404

    cur.execute("SELECT row_to_json(r) FROM (SELECT * FROM user_view where userid = %s) r", (userid,))
    e = cur.fetchone()
    cur.close()
    res_json = json.dumps(e[0], indent=2)
    return res_json, 200


@app.route('/users/<userid>', methods=['PUT'])
def user_update(userid):
    """
    PUT /users/<userid>
        Updates an existing user record. The body of the request should be a valid
        user record. PUTs to a non-existant user should return a 404.
    """
    res = {}
    req = request.get_json(silent=True)
    if not req or not req["userid"] or not req["userid"] == userid:
        abort(400)

    cur = db_conn.cursor()

    cur.execute("SELECT user_exists(%s)", (userid,))
    e = cur.fetchone()
    if e[0] is False:
        return jsonify(res), 404

    array_str = pg_array_string(u'groups', req)
    try:
        cur.execute(
            "SELECT * FROM user_update(%(userid)s, %(first_name)s, %(last_name)s, " + array_str + ")",
            req)
    except Exception, e:
        print "FAIL", e
        cur.close()
        db_conn.rollback()
        return jsonify(res), 400

    e = cur.fetchone()
    db_conn.commit()
    cur.close()
    res_json = json.dumps(e[0], indent=2)
    return res_json, 200, {'Content-Type':'application/json'}



@app.route('/users/<userid>', methods=['DELETE'])
def user_delete(userid):
    """ DELETE /users/<userid> """

    cur = db_conn.cursor()
    res = {}
    cur.execute("SELECT user_exists(%s)", (userid,))
    e = cur.fetchone()
    if e[0] is False:
        return jsonify(res), 404

    cur.execute("SELECT user_delete(%s)", (userid,))
    e = cur.fetchone()
    res["rc"] = e[0]
    db_conn.commit()
    cur.close()
    return jsonify(res), 200






@app.route('/groups', methods=['GET'])
def get_all_groups():
    """ GET /groups """

    cur = db_conn.cursor()
    cur.execute("SELECT row_to_json(r) FROM group_view r")
    e = cur.fetchall()
    if not e or not e[0]:
        return jsonify([]), 200

    cur.close()
    res_json = json.dumps([r[0] for r in e], indent=2)
    return res_json, 200, {'Content-Type':'application/json'}



@app.route('/groups', methods=['POST'])
def group_add():
    """ POST /groups """

    res = {}
    req = request.get_json(silent=True)
    if  not req or not "name" in req:
        return jsonify(res), 400

    cur = db_conn.cursor()

    group_name = req["name"]
    cur.execute("SELECT group_exists(%s)", (group_name,))
    e = cur.fetchone()
    if e[0] is True:
        return jsonify(res), 409

    try:
        cur.execute("SELECT group_add(%s)", (group_name,))
    except Exception, e:
        print "FAIL", e
        cur.close()
        db_conn.rollback()
        return jsonify(res), 400

    e = cur.fetchone()
    db_conn.commit()
    cur.close()
    res_json = json.dumps(e[0], indent=2)
    return res_json, 201, {'Content-Type':'application/json'}


@app.route('/groups/<group_name>', methods=['GET'])
def group_get(group_name):
    """ GET /groups/<group name> """

    cur = db_conn.cursor()
    cur.execute("SELECT group_exists(%s)", (group_name,))
    e = cur.fetchone()
    res = {}
    if e[0] is False:
        return jsonify(res), 404

    cur.execute("SELECT group_get(%s)", (group_name,))
    e = cur.fetchone()
    cur.close()
    db_conn.commit()
    res_json = json.dumps(e[0], indent=2)
    return res_json, 200, {'Content-Type':'application/json'}



@app.route('/groups/<group_name>', methods=['PUT'])
def group_update(group_name):
    """
    PUT /groups/<group name>
        Updates the membership list for the group. The body of the request should
        be a JSON list describing the group's members.
    """
    req = request.get_json(silent=True)
    if  not req or not "name" in req or not req["name"] == group_name:
        abort(400)

    res = {}
    cur = db_conn.cursor()
    cur.execute("SELECT group_exists(%s)", (group_name,))
    e = cur.fetchone()
    if e[0] is False:
        return jsonify(res), 404

    array_str = pg_array_string("users", req)

    try:
        cur.execute("SELECT group_update(%s, " + array_str + ")", (group_name,))
    except Exception, e:
        print "FAIL", e
        cur.close()
        db_conn.rollback()
        return jsonify(res), 400


    e = cur.fetchone()
    db_conn.commit()
    cur.close()
    res_json = json.dumps(e[0], indent=2)
    return res_json, 200, {'Content-Type':'application/json'}



@app.route('/groups/<group_name>', methods=['DELETE'])
def group_delete(group_name):
    """ DELETE /groups/<group name> """

    cur = db_conn.cursor()
    cur.execute("SELECT group_exists(%s)", (group_name,))
    e = cur.fetchone()
    res = {}
    if e[0] is False:
        return jsonify(res), 404

    cur.execute("SELECT group_delete(%s)", (group_name,))
    e = cur.fetchone()
    db_conn.commit()
    cur.close()
    res["rc"] = e[0]
    return jsonify(res), 200


if __name__ == '__main__':
    app.run()
