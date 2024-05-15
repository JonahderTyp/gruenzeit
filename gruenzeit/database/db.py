from __future__ import annotations
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import relationship, backref, Mapped
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Date
from .exceptions import ElementAlreadyExists, ElementDoesNotExsist
from typing import List, Dict
from datetime import datetime
import logging


db = SQLAlchemy()


class dictable:
    def toDict(self) -> dict:
        return {i: getattr(self, i) for i in self.__table__.columns.keys()}


class user_type(db.Model, dictable):
    __tablename__ = 'user_type'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=True)
    users = relationship('user', backref='user_type', lazy=True)


class user(db.Model, UserMixin, dictable):
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


class vehicle(db.Model, dictable):
    __tablename__ = 'vehicle'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(45), nullable=True)
    kennzeichen = Column(String(45), nullable=True)


class job_status(db.Model, dictable):
    __tablename__ = 'job_status'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(45), nullable=True)
    jobs = relationship('job', backref='status')

    @staticmethod
    def getAll() -> dict[int, str]:
        return {i.id: i.name for i in job_status.query.all()}


class job(db.Model, dictable):
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

    @staticmethod
    def getJobs(status: job_status) -> List[job]:
        return job.query.filter_by(status_id=status.id).all()

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


class TimeEntries(db.Model, dictable):
    __tablename__ = 'timeentries'
    id = Column(Integer, primary_key=True, autoincrement=True)
    start_time: datetime = Column(DateTime, nullable=True)
    end_time: datetime = Column(DateTime, nullable=True)
    pause_time: int = Column(Integer, nullable=True)    # in minutes
    user_id = Column(Integer, ForeignKey('user.username'))
    job_id = Column(Integer, ForeignKey('job.id'))
    user: Mapped[user] = relationship('user', backref='time_entries')
    job: Mapped[job] = relationship('job', backref='time_entries')

    @staticmethod
    def newEntry(user: user,
                 start_time: datetime = None,
                 end_time: datetime = None,
                 pause_time: int = 0,
                 job: job | None = None) -> TimeEntries:
        """
        Creates a new time entry in the database.

        Args:
            user (User): The user associated with the time entry.
            start_time (datetime, optional): The start time of the time entry. Defaults to None.
            end_time (datetime, optional): The end time of the time entry. Defaults to None.
            pause_time (int, optional): The pause time in minutes. Defaults to 0.
            job (Job, optional): The job associated with the time entry. Defaults to None.

        Returns:
            TimeEntries: The newly created time entry.

        Raises:
            ValueError: If not all required arguments are set or if start time and end time are not on the same day
                        or if pause time is greater than the timespan between start time and end time.
        """

        if not user or not start_time:
            raise ValueError("Not all required arguments are set")

        if start_time.date() != end_time.date():
            raise ValueError("Start time and end time must be on the same day")

        if start_time > end_time:
            logging.warning("Start time is after end time. Swapping times")
            start_time, end_time = end_time, start_time

        if pause_time > ((end_time - start_time).total_seconds() / 60):
            raise ValueError(
                "Pause time cannot be greater than the timespan between start time and end time")

        new_entry = TimeEntries(
            user_id=user.get_id(),
            start_time=start_time,
            end_time=end_time,
            pause_time=pause_time,
            job_id=job.id if job else None
        )
        print("New Entry", new_entry.toDict())
        db.session.add(new_entry)
        db.session.commit()
        return new_entry

    @staticmethod
    def getEntry(id: int) -> TimeEntries:
        te: TimeEntries = TimeEntries.query.get(id)
        if not te:
            raise ElementDoesNotExsist(
                f"TimeEntry mit der ID {id} existiert nicht")
        return te

    def end(self):
        self.end_time = datetime.now()
        db.session.commit()

    @staticmethod
    def getUnfinishedEntries(usr: user) -> List[TimeEntries]:
        return TimeEntries.query.filter_by(user_id=usr.get_id(), end_time=None).all()

    @staticmethod
    def getEntriesToday(usr: user) -> List[TimeEntries]:
        return TimeEntries.query.filter_by(user_id=usr.get_id()) \
            .filter(TimeEntries.start_time >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)) \
            .order_by(TimeEntries.start_time.asc()).all()


class user_in_vehicle(db.Model, dictable):
    __tablename__ = 'user_in_vehicle'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    vehicle_id = Column(Integer, ForeignKey('vehicle.id'))
    user_id = Column(Integer, ForeignKey('user.username'))
    vehicle = relationship('vehicle', backref='user_in_vehicle')
    user = relationship('user', backref='user_in_vehicle')


class Bild(db.Model, dictable):
    __tablename__ = 'bild'
    id = Column(Integer, primary_key=True, autoincrement=True)
    bild = Column(String(), nullable=True)
    job_id = Column(Integer, ForeignKey('job.id'))
