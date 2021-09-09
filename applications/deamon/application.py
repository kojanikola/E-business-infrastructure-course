from datetime import datetime, timezone

import dateutil.parser
from flask import Flask
from flask_jwt_extended import JWTManager
from redis import Redis

from applications.configuration1 import Configuration
from applications.models import db, Izbori, Validnost, Listic, Ucestvuje

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)


def callback(message):
    splitValue = message.split(',')
    dateNow = dateutil.parser.isoparse(datetime.now(timezone.utc).isoformat())
    dateNow = dateNow.replace(tzinfo=None)
    rows = Izbori.query.all()

    # print(splitValue[1])
    #
    # izboriPom = Ucestvuje.query.filter(Ucestvuje.ucesnikId == splitValue[1]).first()
    #
    # konkretanIzbor = Izbori.query.filter(Izbori.id == izboriPom.izboriId).first()
    #
    # startDate = dateutil.parser.isoparse(konkretanIzbor.datumVremePocetka)
    # endDate = dateutil.parser.isoparse(konkretanIzbor.datumVremeKraja)

    # if not startDate < dateNow and not endDate > dateNow:
    #     print("nisu aktivni")
    #     return

    for IZBOR in rows:

        startDate = dateutil.parser.isoparse(IZBOR.datumVremePocetka)
        endDate = dateutil.parser.isoparse(IZBOR.datumVremeKraja)
        print(startDate)
        print(endDate)
        print(dateNow)

        if not startDate < dateNow and not endDate > dateNow:
            print("nisu aktivni")
            continue
        else:
            # print(splitValue[0])

            glas = Listic.query.filter(Listic.id == splitValue[0]).first()
            # print(glas)

            if glas is not None:
                glas = Listic(id=splitValue[0], redniBr=int(splitValue[1]), jmbg=splitValue[2],
                              izbori_id=IZBOR.id)
                db.session.add(glas)
                db.session.commit()

                validnost = Validnost(listicid=glas.primarykey, razlogid=1)
                db.session.add(validnost);
                db.session.commit();
            else:
                print('usao u else')

                ima = False

                print(IZBOR.id)

                ucesniciNaIzborima = Ucestvuje.query.filter(Ucestvuje.izboriId == IZBOR.id)

                ucesniciNaIzborimaId = []
                for u in ucesniciNaIzborima:
                    ucesniciNaIzborimaId.append(u.ucesnikId)

                print(ucesniciNaIzborimaId)

                for i in ucesniciNaIzborimaId:
                    print(splitValue[1])

                    if int(splitValue[1]) == i:
                        print("nasao")
                        ima = True
                        break

                if ima:
                    glas = Listic(id=splitValue[0], redniBr=int(splitValue[1]), jmbg=splitValue[2],
                                  izbori_id=IZBOR.id)
                    db.session.add(glas)
                    db.session.commit()
                else:
                    print("nije nasao")
                    glas = Listic(id=splitValue[0], redniBr=int(splitValue[1]), jmbg=splitValue[2],
                                  izbori_id=IZBOR.id)
                    db.session.add(glas)
                    db.session.commit()

                    validnost = Validnost(listicid=glas.primarykey, razlogid=2)
                    db.session.add(validnost);
                    db.session.commit();
            break


if __name__ == "__main__":
    db.init_app(application)

    with application.app_context():
        while True:
            with Redis(host='stackF_redis', port=6379) as r:
                _, message = r.blpop(Configuration.REDIS_THREADS_LIST)
                message = message.decode("utf-8")
                callback(message)
