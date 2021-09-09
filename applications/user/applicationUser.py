import csv
import io

from datetime import datetime, timezone
import dateutil.parser
import flask
import redis
from flask import Flask, request, jsonify, make_response
from flask_jwt_extended import JWTManager
from redis import Redis
from sqlalchemy import and_;
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt;
from flask import Response;

from applications.configuration1 import Configuration
from applications.models import db, Listic, Izbori, Ucesnik, Validnost, Razlog, Ucestvuje

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)



def roleCheck(role):
    def innerRole(function):
        @wraps(function)
        def decorator(*arguments, **keywordArguments):
            verify_jwt_in_request();
            claims = get_jwt();
            if ("roles" in claims) and (role in claims["roles"]):
                return function(*arguments, **keywordArguments);
            else:
                return Response("permission denied!", status=403);

        return decorator;

    return innerRole;

@application.route("/vote", methods=["POST"])
@roleCheck(role="Izborni zvanicnik")
def getElections():

    if 'file' not in request.files:
        return make_response(jsonify(message="Field file is missing."), 400)

    content = request.files["file"].stream.read().decode("utf-8")
    stream = io.StringIO(content)
    reader = csv.reader(stream)

    claims = get_jwt()
    jmbg = claims["jmbg"]

    glasovi = []
    i = 0
    for row in reader:
        # glas = Listic(id=row[0], redniBr=int(row[1]))
        # glasovi.append(glas)

        if len(row) < 2:
            return make_response(jsonify(message="Incorrect number of values on line "+str(i)+"."), 400)
        try:
            int(row[1])
        except:
            return make_response(jsonify(message="Incorrect poll number on line " + str(i) + "."), 400)

        if  int(row[1]) < 0:
            return make_response(jsonify(message="Incorrect poll number on line "+str(i)+"."), 400)

        with Redis(host='stackF_redis', port=6379) as r:
            r.rpush(Configuration.REDIS_THREADS_LIST, row[0] + "," + row[1] + "," + jmbg)
        i=i+1

    return flask.Response(status=200)


if __name__ == "__main__":
    db.init_app(application);
    application.run(debug=True, host="0.0.0.0", port=5000)
