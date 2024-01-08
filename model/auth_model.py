from functools import wraps
import mysql.connector
import json, jwt, re
from flask import make_response, request
from config.config import dbconfig

class auth_model:

    def __init__(self):
        try:
            self.con = mysql.connector.connect(host=dbconfig['host'], user=dbconfig['username'], password=dbconfig['password'], database=dbconfig['database'])
            self.con.autocommit = True
            self.cur = self.con.cursor(dictionary=True)
        except:
            print("Some error")

    def token_auth(self, endpoint=""):
        def inner1(func):
            @wraps(func)
            def inner2(*args):
                endpoint = request.url_rule
                authorization = request.headers.get('authorization')
                if re.match("^Bearer *([^ ]+) *$", authorization, flags=0):
                    token = authorization.split(" ")[1]
                    try:
                        token_data = jwt.decode(token, "utkarsh", algorithms="HS256")
                    except jwt.ExpiredSignatureError:
                        return make_response({"error": "Token expired"}, 401)
                    role_id = token_data['payload']['role_id']
                    self.cur.execute(f"SELECT roles FROM accessibility_view WHERE endpoint = '{endpoint}'")
                    result = self.cur.fetchall()
                    if len(result)>0:
                        roles_allowed = json.loads(result[0]['roles'])
                        if role_id in roles_allowed:
                            return func(*args)
                        else:
                            return make_response({"error": "Invalid role"}, 404)
                    else:
                        return make_response({"error": "Unknown endpoint"}, 404)
                else:
                    return make_response({"error": "Invalid token"}, 401)
            return inner2
        return inner1