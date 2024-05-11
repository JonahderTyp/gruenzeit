from __future__ import annotations
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Date
from .exceptions import ElementAlreadyExists, ElementDoesNotExsist
from typing import List, Dict


db = SQLAlchemy()


class user_type(db.Model):
    __tablename__ = 'user_type'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=True)
    users = relationship('user', backref='user_type', lazy=True)


class user(db.Model, UserMixin):
    __tablename__ = 'user'
    username = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=True)
    user_type_id = Column(Integer, ForeignKey('user_type.id'), nullable=True)

    @staticmethod
    def createNew(username: str, name: str, password_hash, user_type_id) -> user:
        if user.query.get(username):
            raise ElementAlreadyExists(
                f"User mit dem Benutzernamen \"{username}\" existiert bereits")
        new_user = user(
            username=username.strip(),
            name=name.strip(),
            password_hash=password_hash,
            user_type_id=user_type_id
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def get_id(self):
        return self.username


class vehicle(db.Model):
    __tablename__ = 'vehicle'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(45), nullable=True)
    kennzeichen = Column(String(45), nullable=True)


class TimeType(db.Model):
    __tablename__ = 'timetype'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(45), nullable=True)


class job_status(db.Model):
    __tablename__ = 'job_status'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(45), nullable=True)
    jobs = relationship('job', backref='status')

    @staticmethod
    def getAll() -> dict[int, str]:
        return {i.id: i.name for i in job_status.query.all()}


class job(db.Model):
    __tablename__ = 'job'
    id = Column(Integer, primary_key=True, autoincrement=True)
    auftragsnummer = Column(String(), nullable=True)
    name = Column(String(), nullable=True)
    adresse = Column(String(), nullable=True)
    beschreibung = Column(String(), nullable=True)
    status_id = Column(Integer, ForeignKey('job_status.id'))
    bilder = relationship('Bild', backref='job')

    @staticmethod
    def createNew(auftragsnummer: str, name: str, adresse: str, beschreibung: str) -> job:
        new_job = job(
            auftragsnummer=auftragsnummer,
            name=name,
            adresse=adresse,
            beschreibung=beschreibung,
            status_id=job_status.query.filter_by(name="In Planung").first().id
        )
        db.session.add(new_job)
        db.session.commit()
        return new_job

    def set_status(self, status: str):
        status = job_status.query.filter_by(name=status).first()
        if not status:
            raise ElementDoesNotExsist(
                f"Status \"{status}\" existiert nicht")
        self.status_id = status.id
        db.session.commit()

    @staticmethod
    def getJob(id: int) -> job:
        bst: job = job.query.get(id)
        if not bst:
            raise ElementDoesNotExsist(
                f"Job mit der ID {id} existiert nicht")
        return bst

    def toHTML(self):
        bst = {
            "id": self.id,
            "auftragsnummer": self.auftragsnummer,
            "name": self.name,
            "adresse": self.adresse,
            "beschreibung": str(self.beschreibung).split("\n"),
            "status": job_status.query.get(self.status_id).name,
            "bilder": [i.bild for i in self.bilder]
        }
        return bst

    def edit(self, auftragsnummer: str, name: str, adresse: str, beschreibung: str):
        db.session.add(self)
        self.auftragsnummer = auftragsnummer
        self.name = name
        self.adresse = adresse
        self.beschreibung = beschreibung
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class TimeEntries(db.Model):
    __tablename__ = 'timeentries'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey('user.username'))
    time_type_id = Column(Integer, ForeignKey('timetype.id'))
    job_id = Column(
        Integer, ForeignKey('job.id'))
    user = relationship('User', backref='time_entries')
    time_type = relationship('TimeType', backref='time_entries')
    job = relationship('job', backref='time_entries')

    @staticmethod
    def getCurrentEntry(user) -> TimeType:
        te: TimeEntries = TimeEntries.query.filter_by(user=user) \
            .order_by(TimeEntries.time.desc()) \
            .first()
        if not te:
            return None
        return TimeType.query.get({"id": te.time_type_id})

    @staticmethod
    def getAvailableEntrys(user: user) -> List[TimeType]:
        types: List[TimeType] = TimeType.query.all()
        current = TimeEntries.getCurrentEntry(user)
        if current is None:
            return [i for i in types if "beginn" in str(i.name).lower()]
        pass


class user_in_vehicle(db.Model):
    __tablename__ = 'user_in_vehicle'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    vehicle_id = Column(Integer, ForeignKey('vehicle.id'))
    user_id = Column(Integer, ForeignKey('user.username'))
    vehicle = relationship('vehicle', backref='user_in_vehicle')
    user = relationship('User', backref='user_in_vehicle')


class Bild(db.Model):
    __tablename__ = 'bild'
    id = Column(Integer, primary_key=True, autoincrement=True)
    bild = Column(String(), nullable=True)
    job_id = Column(Integer, ForeignKey('job.id'))
