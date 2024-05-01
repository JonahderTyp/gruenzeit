from __future__ import annotations
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Date
from .exceptions import ElementAlreadyExists, ElementDoesNotExsist


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


class Baustelle(db.Model):
    __tablename__ = 'baustelle'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=True)


class TimeEntries(db.Model):
    __tablename__ = 'timeentries'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(String(45), nullable=True)
    user_id = Column(Integer, ForeignKey('user.username'))
    time_type_id = Column(Integer, ForeignKey('timetype.id'))
    baustelle_id = Column(
        Integer, ForeignKey('baustelle.id'))
    user = relationship('User', backref='time_entries')
    time_type = relationship('TimeType', backref='time_entries')
    baustelle = relationship('Baustelle', backref='time_entries')


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
    bild = Column(String(45), nullable=True)
    baustellen_id = Column(Integer, ForeignKey('baustelle.id'))
    baustellen = relationship('Baustelle', backref='bilder')
