from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Date
from datetime import datetime
import typing


db = SQLAlchemy()

class Mitarbeiter(db.Model):
    __tablename__ = "mitarbeiter"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

class Team(db.Model):
    __tablename__ = "team"
    id = Column(Integer, primary_key=True)
    team_name = Column(String(255), nullable=False)
    members = relationship("TeamAssignment", back_populates="team")

class TeamAssignment(db.Model):
    __tablename__ = "team_assignment"
    team_id = Column(Integer, ForeignKey('team.id'), primary_key=True)
    employee_id = Column(Integer, ForeignKey('mitarbeiter.id'), primary_key=True)
    date = Column(Date, nullable=False)
    team = relationship("Team", back_populates="members")
    employee = relationship("Mitarbeiter", back_populates="teams")




