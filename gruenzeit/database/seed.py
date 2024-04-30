from .db import Fahrzeug, TimeType, db, Mitarbeiter


def _seed_mitarbeiter():
    mitarbeiter = [Mitarbeiter(name=n) for n in [
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

    _seed_mitarbeiter()

    db.session.commit()
