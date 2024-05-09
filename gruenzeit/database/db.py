from __future__ import annotations
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Date
from .exceptions import ElementAlreadyExists, ElementDoesNotExsist
from typing import List, Dict


db = SQLAlchemy()


class UserType(db.Model):
    __tablename__ = 'usertype'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=True)
    users = relationship('User', backref='usertype', lazy=True)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    username = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=True)
    usertype_id = Column(Integer, ForeignKey('usertype.id'), nullable=True)

    @staticmethod
    def createNew(username: str, name: str, password_hash, usertype_id) -> User:
        if User.query.get(username):
            raise ElementAlreadyExists(
                f"User mit dem Benutzernamen \"{username}\" existiert bereits")
        new_user = User(
            username=username.strip(),
            name=name.strip(),
            password_hash=password_hash,
            usertype_id=usertype_id
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def get_id(self):
        return self.username


class Fahrzeug(db.Model):
    __tablename__ = 'fahrzeug'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(45), nullable=True)
    kennzeichen = Column(String(45), nullable=True)


class TimeType(db.Model):
    __tablename__ = 'timetype'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(45), nullable=True)


class BaustellenStatus(db.Model):
    __tablename__ = 'baustellenstatus'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(45), nullable=True)
    baustellen = relationship('Baustelle', backref='status')

    @staticmethod
    def getAll() -> dict[int, str]:
        return {i.id: i.name for i in BaustellenStatus.query.all()}


class Baustelle(db.Model):
    __tablename__ = 'baustelle'
    id = Column(Integer, primary_key=True, autoincrement=True)
    auftragsnummer = Column(String(), nullable=True)
    name = Column(String(), nullable=True)
    adresse = Column(String(), nullable=True)
    beschreibung = Column(String(), nullable=True)
    status_id = Column(Integer, ForeignKey('baustellenstatus.id'))
    bilder = relationship('Bild', backref='baustellen')

    @staticmethod
    def createNew(auftragsnummer: str, name: str, adresse: str, beschreibung: str) -> Baustelle:
        new_Baustelle = Baustelle(
            auftragsnummer=auftragsnummer,
            name=name,
            adresse=adresse,
            beschreibung=beschreibung,
            status_id=BaustellenStatus.query.filter_by(name="In Planung").first().id
        )
        db.session.add(new_Baustelle)
        db.session.commit()
        return new_Baustelle

    def set_status(self, status: str):
        status = BaustellenStatus.query.filter_by(name=status).first()
        if not status:
            raise ElementDoesNotExsist(
                f"Status \"{status}\" existiert nicht")
        self.status_id = status.id
        db.session.commit()

    @staticmethod
    def getBaustelle(id: int) -> Baustelle:
        bst: Baustelle = Baustelle.query.get(id)
        if not bst:
            raise ElementDoesNotExsist(
                f"Baustelle mit der ID {id} existiert nicht")
        return bst

    def toHTML(self):
        bst = {
            "id": self.id,
            "auftragsnummer": self.auftragsnummer,
            "name": self.name,
            "adresse": self.adresse,
            "beschreibung": str(self.beschreibung).split("\n"),
            "status": BaustellenStatus.query.get(self.status_id).name,
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
    baustelle_id = Column(
        Integer, ForeignKey('baustelle.id'))
    user = relationship('User', backref='time_entries')
    time_type = relationship('TimeType', backref='time_entries')
    baustelle = relationship('Baustelle', backref='time_entries')

    @staticmethod
    def getCurrentEntry(user) -> TimeType:
        te: TimeEntries = TimeEntries.query.filter_by(user=user) \
            .order_by(TimeEntries.time.desc()) \
            .first()
        if not te:
            return None
        return TimeType.query.get({"id": te.time_type_id})

    @staticmethod
    def getAvailableEntrys(user: User) -> List[TimeType]:
        types: List[TimeType] = TimeType.query.all()
        current = TimeEntries.getCurrentEntry(user)
        if current is None:
            return [i for i in types if "beginn" in str(i.name).lower()]
        pass


class FahrzeugAssignments(db.Model):
    __tablename__ = 'fahrzeugassignments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    fahrzeug_id = Column(Integer, ForeignKey('fahrzeug.id'))
    user_id = Column(Integer, ForeignKey('user.username'))
    fahrzeug = relationship('Fahrzeug', backref='assignments')
    user = relationship('User', backref='vehicle_assignments')


class Bild(db.Model):
    __tablename__ = 'bild'
    id = Column(Integer, primary_key=True, autoincrement=True)
    bild = Column(String(), nullable=True)
    baustellen_id = Column(Integer, ForeignKey('baustelle.id'))
