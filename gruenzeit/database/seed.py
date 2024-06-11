import os
from .db import vehicle, db, user, user_type, job_status, job, Bild
from werkzeug.security import generate_password_hash
import random
import logging


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
    user.createNew("g", "Geschäftsführer", generate_password_hash("g"), 2)
    user.createNew("m1", "Mitarbeiter1", generate_password_hash("m1"), 3)
    user.createNew("m2", "Mitarbeiter2", generate_password_hash("m2"), 3)
    user.createNew("m3", "Mitarbeiter3", generate_password_hash("m3"), 3)

    jobs = [
        job.createNew("1234567890", "Betonzaun", "Grüner Weg 1",
                      "Hecke Schneiden\nRasen Schneiden\nVorgarten Pflastern"),
        job.createNew("0987654321", "Terrassenbau Müller", "Blumenstraße 12",
                      "Terrasse bauen\nBeete anlegen\nRasen einsäen"),
        job.createNew("1122334455", "Gartenpflege Schmidt", "Gartenweg 5",
                      "Baum fällen\nSträucher schneiden\nUnkraut jäten"),
        job.createNew("5566778899", "Teichbau Fischer", "Seestraße 8",
                      "Teich ausheben\nTeichfolie verlegen\nBepflanzung um den Teich"),
        job.createNew("2233445566", "Zaunbau Weber", "Holzweg 7",
                      "Holzzaun aufstellen\nPfosten setzen\nGartenweg anlegen"),
        job.createNew("6677889900", "Rasenpflege Schulz",
                      "Wiesenweg 3", "Rasenmähen\nDüngen\nVertikutieren"),
        job.createNew("3344556677", "Baumschnitt Braun", "Baumallee 9",
                      "Obstbäume schneiden\nGartenabfälle entsorgen\nNeuanpflanzungen"),
        job.createNew("7788990011", "Gartenplanung Meier", "Planstraße 4",
                      "Garten planen\nBeete anlegen\nRasenkanten setzen"),
        job.createNew("4455667788", "Landschaftsbau Köhler", "Naturweg 6",
                      "Steingarten anlegen\nTeich gestalten\nWege pflastern")]

    try:
        imgpath = os.path.join(os.path.dirname(__file__), 'images.txt')

        with open(imgpath, 'r') as file:
            lines = [line.strip() for line in file]

        for _job in jobs:
            random_numbers = random.sample(range(len(lines)), random.randint(0, 4))
            for random_number in random_numbers:
                Bild.uploadImage(_job, lines[random_number])
    except Exception as e:
        logging.error("Error while seeding database")
        print(e)

    db.session.commit()
