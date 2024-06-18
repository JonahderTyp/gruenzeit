from __future__ import annotations
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import relationship, backref, Mapped
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Date, Boolean
from .exceptions import ElementAlreadyExists, ElementDoesNotExsist
from typing import List, Dict
from datetime import datetime, date, timedelta
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
    vehicle_id = Column(Integer, ForeignKey('vehicle.id'), nullable=True)

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
    
    @staticmethod
    def getUser(username: str) -> user:
        usr: user = user.query.get(username)
        if not usr:
            raise ElementDoesNotExsist(
                f"User mit dem Benutzernamen \"{username}\" existiert nicht")
        return usr

    def setVehicle(self, vehicle: vehicle | None):
        if vehicle is None:
            self.vehicle_id = None
        else:
            self.vehicle_id = vehicle.id
        db.session.commit()

    def getVehicle(self) -> vehicle:
        return vehicle.query.get(self.vehicle_id)

    def getTeamMembers(self) -> List[user]:
        return user.query.filter_by(vehicle_id=self.vehicle_id).all()

    def get_id(self):
        return self.username


class vehicle(db.Model, dictable):
    __tablename__ = 'vehicle'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(45), nullable=True)
    kennzeichen = Column(String(45), nullable=True)

    @staticmethod
    def newVehicle(name: str, kennzeichen: str) -> vehicle:
        new_vehicle = vehicle(
            name=name,
            kennzeichen=kennzeichen
        )
        db.session.add(new_vehicle)
        db.session.commit()
        return new_vehicle

    @staticmethod
    def getVehicle(id: int) -> vehicle:
        vec: vehicle = vehicle.query.get(id)
        if not vec:
            raise ElementDoesNotExsist(
                f"Fahrzeug mit der ID {id} existiert nicht")
        return vec

    @staticmethod
    def getVehicles() -> List[vehicle]:
        return vehicle.query.all()

    def update(self, name: str, kennzeichen: str) -> None:
        self.name = name
        self.kennzeichen = kennzeichen
        db.session.commit()

    def delete(self) -> None:
        db.session.delete(self)
        db.session.commit()


class job_status(db.Model, dictable):
    __tablename__ = 'job_status'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(45), nullable=True)
    jobs = relationship('job', backref='status')

    @staticmethod
    def getAll() -> dict[int, str]:
        return {i.id: i.name for i in job_status.query.all()}

    @staticmethod
    def get(id: int) -> job_status:
        status = job_status.query.get(id)
        if not status:
            raise ElementDoesNotExsist(
                f"Status mit der ID {id} existiert nicht")
        return status


class job(db.Model, dictable):
    __tablename__ = 'job'
    id = Column(Integer, primary_key=True, autoincrement=True)
    auftragsnummer = Column(String(), nullable=True)
    name = Column(String(), nullable=True)
    adresse = Column(String(), nullable=True)
    beschreibung = Column(String(), nullable=True)
    status_id = Column(Integer, ForeignKey('job_status.id'))
    bilder: Mapped[List[Bild]] = relationship('Bild', backref='job')

    @staticmethod
    def createNew(auftragsnummer: str, name: str, adresse: str, beschreibung: str) -> job:
        new_job = job(
            auftragsnummer=auftragsnummer,
            name=name,
            adresse=adresse,
            beschreibung=beschreibung,
            status_id=job_status.get(1).id
        )
        db.session.add(new_job)
        db.session.commit()
        return new_job

    def set_status(self, statusID: int):
        status = job_status.get(statusID)
        if not status:
            raise ElementDoesNotExsist(
                f"Status \"{statusID}\" existiert nicht")
        self.status_id = status.id
        db.session.commit()

    @staticmethod
    def getJob(id: int | None) -> job:
        if not id:
            return None
        bst: job = job.query.get(id)
        if not bst:
            raise ElementDoesNotExsist(
                f"Job mit der ID {id} existiert nicht")
        return bst

    @staticmethod
    def getJobs(status: job_status | None = None) -> List[job]:
        if not status:
            return job.query.all()
        return job.query.filter_by(status_id=status.id).all()
    
    def getTimestamps(self) -> List[TimeEntries]:
        # Return all timestamps for this job
        return TimeEntries.query.filter_by(job_id=self.id).all()

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
    is_team_entry = Column(Boolean, default=False)
    user: Mapped[user] = relationship('user', backref='time_entries')
    job: Mapped[job] = relationship('job', backref='time_entries')

    @staticmethod
    def newEntry(user: user,
                 start_time: datetime = None,
                 end_time: datetime = None,
                 pause_time: int = 0,
                 job: job | None = None,
                 is_team_entry: bool = False,
                 _prevent_reqursion: bool = False) -> TimeEntries:
        """
        Creates a new time entry in the database.

        Args:
            user (User): The user associated with the time entry.
            start_time (datetime, optional): The start time of the time entry. Defaults to None.
            end_time (datetime, optional): The end time of the time entry. Defaults to None.
            pause_time (int, optional): The pause time in minutes. Defaults to 0.
            job (Job, optional): The job associated with the time entry. Defaults to None.
            is_team_entry (bool, optional): Indicates if the entry is for the team. Defaults to False.

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
            job_id=job.id if job else None,
            is_team_entry=is_team_entry
        )
        print("New Entry", new_entry.toDict())
        db.session.add(new_entry)
        db.session.commit()

        if is_team_entry and not _prevent_reqursion:
            team_members = user.getTeamMembers()
            for member in team_members:
                if member.username != user.username:  # Avoid duplicating the entry for the user
                    TimeEntries.newEntry(
                        member, start_time, end_time, pause_time, job, True, True)
        return new_entry

    def edit(self, start_time: datetime, end_time: datetime, pause_time: int, job: job | None, is_team_entry: bool = False, _prevent_reqursion: bool = False):
        if start_time.date() != end_time.date():
            raise ValueError("Start time and end time must be on the same day")

        if start_time > end_time:
            logging.warning("Start time is after end time. Swapping times")
            start_time, end_time = end_time, start_time

        if pause_time > ((end_time - start_time).total_seconds() / 60):
            raise ValueError(
                "Pause time cannot be greater than the timespan between start time and end time")

        original_start_time = self.start_time
        original_end_time = self.end_time
        original_pause_time = self.pause_time
        original_job_id = self.job_id

        self.start_time = start_time
        self.end_time = end_time
        self.pause_time = pause_time
        self.job_id = job.id if job else None
        self.is_team_entry = is_team_entry
        db.session.commit()

        if is_team_entry and not _prevent_reqursion:
            team_members = self.user.getTeamMembers()
            for member in team_members:
                if member.username != self.user.username:  # Avoid duplicating the entry for the user
                    existing_entrys: List[TimeEntries] = TimeEntries.query.filter_by(
                        user_id=member.username,
                        start_time=original_start_time,
                        end_time=original_end_time,
                        pause_time=original_pause_time,
                        job_id=original_job_id,
                        is_team_entry=self.is_team_entry).all()
                    if len(existing_entrys) == 1:
                        existing_entrys[0].edit(
                            self.start_time, self.end_time, self.pause_time, job.getJob(self.job_id), True, True)
                    elif len(existing_entrys) > 1:
                        print(
                            "There are multiple entries for the same time. This should not happen")
                        
    def getWorkTime(self) -> timedelta:
        return (self.end_time if self.end_time else datetime.now()) - self.start_time - timedelta(minutes=self.pause_time)

    @staticmethod
    def getEntry(id: int) -> TimeEntries:
        te: TimeEntries = TimeEntries.query.get(id)
        if not te:
            raise ElementDoesNotExsist(
                f"TimeEntry mit der ID {id} existiert nicht")
        return te

    @staticmethod
    def getEntriesToday(usr: user) -> List[TimeEntries]:
        return TimeEntries.query.filter_by(user_id=usr.get_id()) \
            .filter(TimeEntries.start_time >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)) \
            .order_by(TimeEntries.start_time.asc()).all()

    @staticmethod
    def getEntriesOfDate(date: date = date.today()) -> List[TimeEntries]:
        return TimeEntries.query \
            .filter(TimeEntries.start_time >= datetime.combine(date, datetime.min.time())) \
            .filter(TimeEntries.start_time <= datetime.combine(date, datetime.max.time())) \
            .order_by(TimeEntries.start_time.asc()).all()


class Bild(db.Model, dictable):
    __tablename__ = 'bild'
    id = Column(Integer, primary_key=True, autoincrement=True)
    bild = Column(String(), nullable=True)
    job_id = Column(Integer, ForeignKey('job.id'))

    @staticmethod
    def uploadImage(job: job, bild: str):
        new_bild = Bild(
            bild=bild,
            job_id=job.id
        )
        db.session.add(new_bild)
        db.session.commit()
        return new_bild

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def getBild(id: int) -> Bild:
        bild: Bild = Bild.query.get(id)
        if not bild:
            raise ElementDoesNotExsist(
                f"Bild mit der ID {id} existiert nicht")
        return bild

    @staticmethod
    def getBilder(job: job) -> List[Bild]:
        return Bild.query.filter_by(job_id=job.id).all()
