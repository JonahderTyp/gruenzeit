import os
import logging
from flask import Flask
from flask_login import LoginManager
from pathlib import Path
from .database.seed import seed_database
from .database.db import user


def create_app():
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logging.info("Creating App")

    INSTANCE_PATH = os.path.abspath(os.path.join(
        os.path.abspath(__path__[0]), "../instance"))

    app = Flask(__name__, instance_path=INSTANCE_PATH)

    config_path = Path(app.instance_path) / 'config.cfg'

    if config_path.is_file():
        app.config.from_pyfile(str(config_path))
        logging.info("Loaded TEST configuration from {}".format(config_path))
        logging.info("Configuration:")
        logging.info(str(app.config))
    else:
        logging.warning(
            "Configuration file not found at {}".format(config_path))
        
    # app.config['SESSION_COOKIE_SECURE'] = False
    # app.config['SQLALCHEMY_ECHO'] = True

    app.config['WTF_CSRF_ENABLED'] = True

    from .database import db
    db.init_app(app)

    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'site.login'

    @login_manager.user_loader
    def user_loader(user_id):
        return user.query.get(user_id)

    with app.app_context():
        db.create_all()

        # Check if every Table is empty
        NEW_DB = all(db.session.query(table).first()
                     is None for table in db.metadata.sorted_tables)

        if NEW_DB:
            logging.info("All tables are empty. Seeding database...")
            seed_database()

    from .site import site
    app.register_blueprint(site)

    # logging.info(app.config)

    return app
