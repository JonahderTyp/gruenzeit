import os
import logging
from flask import Flask
from pathlib import Path


def create_app():
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logging.info("Creating App")

    INSTANCE_PATH = os.path.abspath(os.path.join(os.path.abspath(__path__[0]), "../instance"))

    app = Flask(__name__, instance_path=INSTANCE_PATH)

    config_path = Path(app.instance_path) / 'config.cfg'

    if config_path.is_file():
        app.config.from_pyfile(str(config_path))
        logging.info("Loaded configuration from {}".format(config_path))
    else:
        logging.warning(
            "Configuration file not found at {}".format(config_path))

    from .site import site
    app.register_blueprint(site)

    logging.info(app.config)

    return app
