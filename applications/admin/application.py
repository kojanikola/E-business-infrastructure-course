from datetime import datetime

from dateutil import parser
from flask import Flask, request, jsonify, make_response
from flask_jwt_extended import JWTManager
from pytz import utc

from datetime import datetime, timezone
import dateutil.parser

from adminDecorator import roleCheck
from applications.configuration1 import Configuration
from applications.models import db, Ucesnik, Ucestvuje, Listic, Razlog, Validnost, Izbori
import json
from sqlalchemy import and_;

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)


@application.route("/createParticipant", methods=["POST"])
@roleCheck(role="Admin")
def createParticipant():
    name = request.json.get("name")
    individual = request.json.get("individual")

    if name is None:
        data = {"message": "Field name is missing."}
        return jsonify(data), 400

    nameEmpty = len(name) == 0

    if nameEmpty:
        data = {"message": "Field name is missing."}
        return jsonify(data), 400

    if individual is None:
        data = {"message": "Field individual is missing."}
        return jsonify(data), 400

    postojeciUcesnik = Ucesnik.query.filter_by(name=name).first()

    if postojeciUcesnik:
        print("ucesnik postoji")
        # data = {"message": "Ucesnik vec postoji"}
        # data = {"message": "Ucesnik vec postoji"}
        # return jsonify(data), 400

    ucesnik = Ucesnik(name=name, tip=individual)

    db.session.add(ucesnik)
    db.session.commit()

    data = {"id": ucesnik.id}
    return jsonify(data), 200


@application.route("/getParticipants", methods=["GET"])
@roleCheck(role="Admin")
def getParticipants():
    participants = Ucesnik.query.all()

    pom = []

    map = {}

    for p in participants:
        map["id"] = p.id
        map["name"] = p.name
        map["individual"] = p.tip
        pom.append(map)
        map = {}

    return make_response(jsonify(participants=pom), 200)


@application.route("/createElection", methods=["POST"])
@roleCheck(role="Admin")
def createElection():
    print("aaa")
    start = request.json.get("start")
    end = request.json.get("end")
    individual = request.json.get("individual")
    participants = request.json.get("participants")

    # startMissing = len(start) == 0
    # endMissing = len(end) == 0

    if (start is None or len(start) == 0):
        print("starterror")
        data = {"message": "Field start is missing."}
        return jsonify(data), 400

    if end is None or len(end) == 0:
        print("enderror")
        data = {"message": "Field end is missing."}
        return jsonify(data), 400

    if individual is None or individual == '':
        print("indvError")
        data = {"message": "Field individual is missing."}
        return jsonify(data), 400

    if participants is None or participants == '':
        print("participantsError")
        data = {"message": "Field participants is missing."}
        return jsonify(data), 400

    try:
        datumStart = parser.isoparse(start)
        datumEnd = parser.isoparse(end);

        startDate = datumStart.replace(tzinfo=utc)
        endDate = datumEnd.replace(tzinfo=utc)
    except:
        data = {"message": "Invalid date and time."}
        return jsonify(data), 400

    if startDate > endDate:
        print("datum van")
        data = {"message": "Invalid date and time."}
        return jsonify(data), 400

    izbori = Izbori.query.all()

    for i in izbori:
        vremePocetkaI = parser.isoparse(i.datumVremePocetka)
        vremeKrajaI = parser.isoparse(i.datumVremeKraja)

        vremePocetkaI = vremePocetkaI.replace(tzinfo=utc)
        vremeKrajaI = vremeKrajaI.replace(tzinfo=utc)

        if (startDate > vremePocetkaI and startDate < vremeKrajaI) or (
                endDate > vremePocetkaI and endDate < vremeKrajaI):
            data = {"message": "Invalid date and time."}
            return jsonify(data), 400

    # try:
    #     datumStart = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S%z")
    # except:
    #     print("startdateError")
    #     data = {"message": "Invalid date and time."}
    #     return jsonify(data), 400
    #
    # try:
    #     datumEnd = datetime.strptime(end, "%Y-%m-%dT%H:%M:%S%z")
    # except:
    #     print("enddateError")
    #     data = {"message": "Invalid date and time."}
    #     return jsonify(data), 400

    if len(participants) < 2:
        print("part manje")
        data = {"message": "Invalid participants."}
        return jsonify(data), 400

    participantsQ = Ucesnik.query.filter(Ucesnik.tip == individual)

    participantsID = []

    for partQ in participantsQ:
        participantsID.append(partQ.id)

    for p in participants:
        if p not in participantsID:
            print("participant van mere")
            data = {"message": "Invalid participants."}
            return jsonify(data), 400

    election = Izbori(datumVremePocetka=start, datumVremeKraja=end, tip=individual)
    db.session.add(election)
    db.session.commit()

    listic = []
    i = 0

    for u in participants:
        ucestvuje = Ucestvuje(ucesnikId=u, izboriId=election.id, pollId=i + 1)
        db.session.add(ucestvuje)
        db.session.commit()
        listic.append(i + 1)
        i = i + 1

    data = {"pollNumbers": listic}
    return jsonify(data), 200


@application.route("/getElections", methods=["GET"])
@roleCheck(role="Admin")
def getElections():
    # return json.dumps([u.as_dict() for u in Izbori.query.all()])
    izbori = Izbori.query.all()
    pom = []
    map = {}
    for i in izbori:
        map["id"] = i.id
        map["start"] = i.datumVremePocetka
        map["end"] = i.datumVremeKraja
        map["individual"] = i.tip
        participants = Ucesnik.query.join(Ucestvuje).filter(Ucestvuje.izboriId == i.id)
        mapParticipants = {}
        pomParticipants = []

        for p in participants:
            mapParticipants["id"] = p.id
            mapParticipants["name"] = p.name
            pomParticipants.append(mapParticipants)
            mapParticipants = {}

        map["participants"] = pomParticipants
        pom.append(map)
        map = {}

    return make_response(jsonify(elections=pom), 200)


@application.route("/", methods=["GET"])
def dummy():
    print("Hello")


@application.route("/getResults", methods=["GET"])
@roleCheck(role="Admin")
def getResults():
    id = (request.args.get("id", ""))

    if len(id) == 0 or id == '':
        data = {"message": "Field id is missing."}
        return jsonify(data), 400

    izbori = Izbori.query.filter(Izbori.id == id).first()

    if izbori is None:
        data = {"message": "Election does not exist."}
        return jsonify(data), 400

    startDate = dateutil.parser.isoparse(izbori.datumVremePocetka)
    endDate = dateutil.parser.isoparse(izbori.datumVremeKraja)

    dateNow = dateutil.parser.isoparse(datetime.now(timezone.utc).isoformat())
    dateNow = dateNow.replace(tzinfo=utc)
    startDate = startDate.replace(tzinfo=utc)
    endDate = endDate.replace(tzinfo=utc)

    print(startDate)
    print(endDate)
    print(dateNow)

    if startDate < dateNow < endDate:
        data = {"message": "Election is ongoing."}
        return jsonify(data), 400

    nevazeciGlasovi = db.session.query(Validnost).order_by(Validnost.listicid)
    nevazeciGlasiviID = []

    for nG in nevazeciGlasovi:
        nevazeciGlasiviID.append(nG.listicid)

    ucesniciRet = []
    if izbori.tip:
        ucesnici = db.session.query(Ucestvuje.ucesnikId).filter(Ucestvuje.izboriId == izbori.id)
        mapa = {}

        sviGlasovi = Listic.query.all()

        vazeciGlasovi = []
        for glas in sviGlasovi:
            if not glas.id in nevazeciGlasiviID:
                vazeciGlasovi.append(glas)

        ukupanRezultat = 0

        for u in ucesnici:
            ucesnik = Ucesnik.query.filter(Ucesnik.id == u.ucesnikId).first()
            mapa["pollNumber"] = u[0]
            mapa["name"] = ucesnik.name
            ucestvuje = Ucestvuje.query.filter(
                and_(Ucestvuje.ucesnikId == ucesnik.id, Ucestvuje.izboriId == izbori.id)).first()
            result = 0
            for vg in vazeciGlasovi:
                if vg.redniBr == ucestvuje.pollId and vg.izbori_id == izbori.id:
                    result = result + 1
            ukupanRezultat = ukupanRezultat + result
            mapa["result"] = result
            ucesniciRet.append(mapa)
            mapa = {}

        for rez in ucesniciRet:
            rez["result"] = round(1.0 * rez["result"] / ukupanRezultat,2)
    else:
        print("usao")
        ucesnici = db.session.query(Ucestvuje.ucesnikId).filter(Ucestvuje.izboriId == izbori.id)
        mapa = {}

        sviGlasovi = Listic.query.all()

        vazeciGlasovi = []
        for glas in sviGlasovi:
            if not glas.id in nevazeciGlasiviID:
                vazeciGlasovi.append(glas)

        ukupanRezultat = 0

        for u in ucesnici:
            ucesnik = Ucesnik.query.filter(Ucesnik.id == u.ucesnikId).first()
            mapa["pollNumber"] = u[0]
            mapa["name"] = ucesnik.name
            ucestvuje = Ucestvuje.query.filter(
                and_(Ucestvuje.ucesnikId == ucesnik.id, Ucestvuje.izboriId == izbori.id)).first()
            result = 0
            for vg in vazeciGlasovi:
                if vg.redniBr == ucestvuje.pollId and vg.izbori_id == izbori.id:
                    result = result + 1
            ukupanRezultat = ukupanRezultat + result
            mapa["result"] = result
            ucesniciRet.append(mapa)
            mapa = {}

        konacni = []

        for u in ucesniciRet:
            print(u["result"])
            if u["result"] > 0.05 * ukupanRezultat:
                konacni.append(u)

        print(konacni[0])

        rezultati = []
        deli = []
        max = 0
        for i in konacni:
            rezultati.append(i["result"])
            print(i["result"])
            deli.append(2)
            if i["result"] > max:
                max = i["result"]
            i["result"] = 0

        print(rezultati[0])
        print(deli[0])
        print(max)

        k = 0

        for k in range(250):
            index = 0
            while index < rezultati[index]:
                index = index + 1
            konacni[index]["result"] = rezultati[index] / deli[index]
            deli[index] = deli[index] + 1
            max = 0
            for i in konacni:
                if i["result"] > max:
                    max = i["result"]

    razloziRet = []
    for ng in nevazeciGlasovi:
        glas = Listic.query.filter(Listic.primarykey == ng.listicid).first()
        mapa["electionOfficialJmbg"] = glas.jmbg
        mapa["ballotGuid"] = glas.id
        mapa["pollNumber"] = glas.redniBr
        mapa["reason"] = Razlog.query.filter(Razlog.id == ng.razlogid).first().tip
        result = 0
        for vg in vazeciGlasovi:
            if vg.id not in nevazeciGlasiviID and vg.redniBr == ucesnik.id:
                result = result + 1
        razloziRet.insert(0, mapa)
        mapa = {}

    return jsonify(participants=ucesniciRet, invalidVotes=razloziRet), 200


if __name__ == "__main__":
    db.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5001)
