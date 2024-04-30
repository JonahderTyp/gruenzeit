from .db import Fahrzeug, TimeType, db, User, UserType
from werkzeug.security import generate_password_hash

def _seed_mitarbeiter():
    mitarbeiter = [User(name=n) for n in [
        "Lena Schröder",
        "Tobias Müller",
        "Katharina Vogel",
        "Felix Richter",
        "Martina Fischer",
        "Niklas Weber",
        "Julia Koch",
        "Sven Meier",
        "Anja Krause",
        "David Lehmann",
    ]]
    db.session.bulk_save_objects(mitarbeiter)


def seed_database():
    print("Seeding Database")
    timeTypes = [
        TimeType(id=1, name="Arbeit-beginn"),
        TimeType(id=2, name="Pause-beginn"),
        TimeType(id=3, name="Pause-ende"),
        TimeType(id=4, name="Arbeit-ende"),
    ]
    db.session.bulk_save_objects(timeTypes)

    fahrzeuge = [
        Fahrzeug(id=1, name="Fahrzeug1", kennzeichen="BE JW 1"),
        Fahrzeug(id=2, name="Fahrzeug2", kennzeichen="BE JW 2"),
    ]
    db.session.bulk_save_objects(fahrzeuge)

    userTypes = [
        UserType(id=1, name="admin"),
        UserType(id=2, name="Geschäftsführer"),
        UserType(id=3, name="Mitarbeiter"),
    ]
    db.session.bulk_save_objects(userTypes)

    # _seed_mitarbeiter()

    User.createNew("admin", "admin", generate_password_hash("admin"), 1)

    db.session.commit()
