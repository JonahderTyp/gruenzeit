from .db import vehicle, db, user, user_type, job_status, job
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
        job_status(id=1, name="In Bearbeitung"),
        job_status(id=2, name="Abgeschlossen"),
    ]
    db.session.bulk_save_objects(baustellenStatus)

    # _seed_mitarbeiter()

    user.createNew("admin", "admin", generate_password_hash("admin"), 1)

    job.createNew("1234567890", "Betonzaun", "Grüner Weg 1",
                  "Hecke Schneiden\nRasen Schneiden\nVorgarten Pflastern")
    job.createNew("0987654321", "Terrassenbau Müller", "Blumenstraße 12",
                  "Terrasse bauen\nBeete anlegen\nRasen einsäen")
    job.createNew("1122334455", "Gartenpflege Schmidt", "Gartenweg 5",
                  "Baum fällen\nSträucher schneiden\nUnkraut jäten")
    job.createNew("5566778899", "Teichbau Fischer", "Seestraße 8",
                  "Teich ausheben\nTeichfolie verlegen\nBepflanzung um den Teich")
    job.createNew("2233445566", "Zaunbau Weber", "Holzweg 7",
                  "Holzzaun aufstellen\nPfosten setzen\nGartenweg anlegen")
    job.createNew("6677889900", "Rasenpflege Schulz",
                  "Wiesenweg 3", "Rasenmähen\nDüngen\nVertikutieren")
    job.createNew("3344556677", "Baumschnitt Braun", "Baumallee 9",
                  "Obstbäume schneiden\nGartenabfälle entsorgen\nNeuanpflanzungen")
    job.createNew("7788990011", "Gartenplanung Meier", "Planstraße 4",
                  "Garten planen\nBeete anlegen\nRasenkanten setzen")
    job.createNew("4455667788", "Landschaftsbau Köhler", "Naturweg 6",
                  "Steingarten anlegen\nTeich gestalten\nWege pflastern")

    db.session.commit()
