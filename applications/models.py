from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

from sqlalchemy import ForeignKey

db = SQLAlchemy()

class Validnost(db.Model):
    __tablename__ = "validnost"
    id = db.Column(db.Integer, primary_key=True)
    razlogid = db.Column(db.Integer, db.ForeignKey("razlozi.id"), nullable=False)
    listicid = db.Column(db.Integer, db.ForeignKey("listici.primarykey"), nullable=False)

class Listic(db.Model):
    __tablename__ = "listici"
    primarykey = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(256), nullable=False)
    redniBr = db.Column(db.Integer, nullable=False)
    jmbg = db.Column(db.String(13), nullable=False)
    razlozi = db.relationship("Razlog", secondary=Validnost.__table__, back_populates="listici")
    izbori_id = db.Column(db.Integer, db.ForeignKey("izbori.id"))


class Razlog(db.Model):
    __tablename__ = "razlozi"
    id = db.Column(db.Integer, primary_key=True)
    tip = db.Column(db.String(256), nullable=False)
    listici = db.relationship("Listic", secondary=Validnost.__table__, back_populates="razlozi")



class Ucestvuje(db.Model):
    __tablename__ = "ucestvuje"
    id = db.Column(db.Integer, primary_key=True)
    ucesnikId = db.Column(db.Integer, db.ForeignKey("ucesnici.id"), nullable=False)
    izboriId = db.Column(db.Integer, db.ForeignKey("izbori.id"), nullable=False)
    pollId = db.Column(db.Integer, nullable=False)


class Izbori(db.Model):
    __tablename__ = "izbori"
    id = db.Column(db.Integer, primary_key=True)
    datumVremePocetka = db.Column(db.String(256), nullable=False)
    datumVremeKraja = db.Column(db.String(256), nullable=False)
    tip = db.Column(db.Boolean, nullable=False)
    ucesnici = db.relationship("Ucesnik", secondary=Ucestvuje.__table__, back_populates="izbori")
    listici = db.relationship("Listic", backref="listic")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class JsonModel(object):
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Ucesnik(db.Model):
    __tablename__ = "ucesnici"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    tip = db.Column(db.Boolean, nullable=False)
    izbori = db.relationship("Izbori", secondary=Ucestvuje.__table__, back_populates="ucesnici")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return self.id, self.name, self.tip


class Glas(db.Model):
    __tablename__ = "glasovi"
    id = db.Column(db.String(256), primary_key=True)
    jmbg = db.Column(db.String(13), nullable=False)
