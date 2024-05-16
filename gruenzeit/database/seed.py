from .db import vehicle, db, user, user_type, job_status
from werkzeug.security import generate_password_hash

def _seed_mitarbeiter():
    mitarbeiter = [user(name=n) for n in [
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

    fahrzeuge = [
        vehicle(id=1, name="Fahrzeug1", kennzeichen="BE JW 1"),
        vehicle(id=2, name="Fahrzeug2", kennzeichen="BE JW 2"),
    ]
    db.session.bulk_save_objects(fahrzeuge)

    userTypes = [
        user_type(id=1, name="admin"),
        user_type(id=2, name="Geschäftsführer"),
        user_type(id=3, name="Mitarbeiter"),
    ]
    db.session.bulk_save_objects(userTypes)

    baustellenStatus = [
        job_status(id=1, name="In Planung"),
        job_status(id=2, name="In Bearbeitung"),
        job_status(id=3, name="Abgeschlossen"),
    ]
    db.session.bulk_save_objects(baustellenStatus)

    # _seed_mitarbeiter()

    user.createNew("admin", "admin", generate_password_hash("admin"), 1)

    db.session.commit()
