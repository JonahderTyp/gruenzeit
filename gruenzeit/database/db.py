from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Date
from datetime import datetime
import typing


db = SQLAlchemy()


class Mitarbeiter(db.Model):
    __tablename__ = 'mitarbeiter'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=True)


class Fahrzeug(db.Model):
    __tablename__ = 'fahrzeug'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(45), nullable=True)
    kennzeichen = Column(String(45), nullable=True)


class TimeType(db.Model):
    __tablename__ = 'timetype'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(45), nullable=True)


class Baustellen(db.Model):
    __tablename__ = 'baustellen'
    id = Column(Integer, primary_key=True)
    baustellencol = Column(String(45), nullable=True)


class TimeEntries(db.Model):
    __tablename__ = 'timeentries'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(String(45), nullable=True)
    mitarbeiter_id = Column(Integer, ForeignKey('mitarbeiter.id'))
    time_type_id = Column(Integer, ForeignKey('timetype.id'))
    baustellen_id = Column(
        Integer, ForeignKey('baustellen.id'))
    mitarbeiter = relationship('Mitarbeiter', backref='time_entries')
    time_type = relationship('TimeType', backref='time_entries')
    baustellen = relationship('Baustellen', backref='time_entries')
  

class FahrzeugAssignments(db.Model):
    __tablename__ = 'fahrzeugassignments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    team_id = Column(Integer, ForeignKey('fahrzeug.id'))
    mitarbeiter_id = Column(Integer, ForeignKey('mitarbeiter.id'))
    fahrzeug = relationship('Fahrzeug', backref='assignments')
    mitarbeiter = relationship('Mitarbeiter', backref='vehicle_assignments')


class Bild(db.Model):
    __tablename__ = 'bild'
    id = Column(Integer, primary_key=True, autoincrement=True)
    bild = Column(String(45), nullable=True)
    baustellen_id = Column(Integer, ForeignKey('baustellen.id'))
    baustellen = relationship('Baustellen', backref='bilder')
