from functools import wraps

from flask import Flask, request, Response
from configuration import Configuration
from models import db, User, UserRole
from email.utils import parseaddr
import re
from flask import jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, \
    get_jwt_identity, verify_jwt_in_request;
from sqlalchemy import and_;

application = Flask(__name__);
application.config.from_object(Configuration);


def checkJmbg(jmbg):
    if (int(jmbg[0:2]) < 1 or int(jmbg[0:2]) > 31):
        return False
    if (int(jmbg[2:4]) < 1 or int(jmbg[2:4]) > 12):
        return False
    if (int(jmbg[4:7]) < 0 or int(jmbg[4:7]) > 999):
        return False
    if (int(jmbg[7:9]) < 70 or int(jmbg[7:9]) > 99):
        return False
    if (int(jmbg[9:12]) > 999):
        return False

    a = int(jmbg[0])
    b = int(jmbg[1])
    c = int(jmbg[2])
    d = int(jmbg[3])
    e = int(jmbg[4])
    f = int(jmbg[5])
    g = int(jmbg[6])
    h = int(jmbg[7])
    i = int(jmbg[8])
    j = int(jmbg[9])
    k = int(jmbg[10])
    l = int(jmbg[11])
    m = int(jmbg[12])

    mFla = 11 - ((7 * (a + g) + 6 * (b + h) + 5 * (c + i) + 4 * (d + j) + 3 * (e + k) + 2 * (f + l)) % 11)

    if (m != mFla):
        return False
    return True


def checkPassword(password):
    flag = 0
    while True:
        if (len(password) < 8):
            flag = -1
            break
        elif not re.search("[a-z]", password):
            flag = -1
            break
        elif not re.search("[A-Z]", password):
            flag = -1
            break
        elif not re.search("[0-9]", password):
            flag = -1
            break
        # elif not re.search("[_@$]", password):
        #     flag = -1
        #     break
        elif re.search("\s", password):
            flag = -1
            break
        else:
            flag = 0
            print("Valid Password")
            break
    if flag == -1:
        return False
    return True


@application.route("/register", methods=["POST"])
def register():
    email = request.json.get("email", "");
    password = request.json.get("password", "");
    forename = request.json.get("forename", "");
    surname = request.json.get("surname", "");
    jmbg = request.json.get("jmbg", "")

    emailEmpty = len(email) == 0;
    passwordEmpty = len(password) == 0;
    forenameEmpty = len(forename) == 0;
    surnameEmpty = len(surname) == 0;
    jmbgEmpty = len(jmbg) == 0;

    user = User.query.filter(User.email == email).first()

    if jmbgEmpty:
        data = {"message": "Field jmbg is missing."}
        return jsonify(data), 400

    if forenameEmpty:
        data = {"message": "Field forename is missing."}
        return jsonify(data), 400

    if surnameEmpty:
        data = {"message": "Field surname is missing."}
        return jsonify(data), 400

    if emailEmpty:
        data = {"message": "Field email is missing."}
        return jsonify(data), 400

    if passwordEmpty:
        data = {"message": "Field password is missing."}
        return jsonify(data), 400

    if (len(jmbg) < 13 or len(jmbg) > 13 or not checkJmbg(jmbg)):
        data = {"message": "Invalid jmbg."}
        return jsonify(data), 400

    result = parseaddr(email)

    if len(result[1]) == 0:
        data = {"message": "Invalid email."}
        return jsonify(data), 400

    if not re.match(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}", email):
        data = {"message": "Invalid email."}
        return jsonify(data), 400

    if not checkPassword(password):
        data = {"message": "Invalid password."}
        return jsonify(data), 400

    if user:
        data = {"message": "Email already exists."}
        return jsonify(data), 400

    user = User(email=email, password=password, ime=forename, prezime=surname, jmbg=jmbg)
    db.session.add(user)
    db.session.commit()

    userRole = UserRole(userId=user.id, roleId=2);
    db.session.add(userRole)
    db.session.commit()

    return Response("Registration successful!", status=200);


jwt = JWTManager(application);


@application.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    emailEmpty = len(email) == 0
    passwordEmpty = len(password) == 0

    if emailEmpty:
        data = {"message": "Field email is missing."}
        return jsonify(data), 400

    if passwordEmpty:
        data = {"message": "Field password is missing."}
        return jsonify(data), 400

    user = User.query.filter(and_(User.email == email, User.password == password)).first()

    if user:
        print(user.email);

    if not re.match(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}", email):
        data = {"message": "Invalid email."}
        return jsonify(data), 400

    result = parseaddr(email)

    if len(result[1]) == 0:
        data = {"message": "Invalid email."}
        return jsonify(data), 400

    if not user:
        data = {"message": "Invalid credentials."}
        return jsonify(data), 400

    additionalClaims = {
        "forename": user.ime,
        "surname": user.prezime,
        "jmbg": user.jmbg,
        "roles": [str(role) for role in user.roles]
    }

    accessToken = create_access_token(identity=user.email, additional_claims=additionalClaims);
    refreshToken = create_refresh_token(identity=user.email, additional_claims=additionalClaims);

    return jsonify(accessToken=accessToken, refreshToken=refreshToken), 200


@application.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    refreshClaims = get_jwt()

    additionalClaims = {
        "forename": refreshClaims["forename"],
        "surname": refreshClaims["surname"],
        "roles": refreshClaims["roles"],
        "jmbg": refreshClaims["jmbg"]
    }

    refreshToken = create_access_token(identity=identity, additional_claims=additionalClaims);

    return jsonify(accessToken=refreshToken), 200


def roleCheck(role):
    def innerRole(function):
        @wraps(function)
        def decorator(*arguments, **keywordArguments):
            verify_jwt_in_request();
            claims = get_jwt();
            if (("roles" in claims) and (role in claims["roles"])):
                return function(*arguments, **keywordArguments);
            else:
                return Response("permission denied!", status=403);

        return decorator;

    return innerRole;


@application.route("/delete", methods=["POST"])
@jwt_required()
@roleCheck(role="Admin")
def delete():
    additionalClaims = get_jwt()
    roles = additionalClaims["roles"]

    email = request.json.get("email", "")

    result = parseaddr(email)

    if len(email) == 0:
        data = {"message": "Field email is missing."}
        return jsonify(data), 400

    if len(result[1]) == 0:
        data = {"message": "Invalid email."}
        return jsonify(data), 400

    if not re.match(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}", email):
        data = {"message": "Invalid email."}
        return jsonify(data), 400

    user = User.query.filter(User.email == email).first()

    if not user:
        data = {"message": "Unknown user."}
        return jsonify(data), 400
    else:
        db.session.delete(user)
        db.session.commit()
        data = {"message": "Deleted successfully"}
        return jsonify(data), 200


@application.route("/", methods=["GET"])
def index():
    return "Hello world!";


if (__name__ == "__main__"):
    db.init_app(application);
    application.run(debug=True, host="0.0.0.0", port=5002)
