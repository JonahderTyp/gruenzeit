import os
from secrets import token_urlsafe
from pathlib import Path


def generate_config_file(instance_folder: Path):
    configFile = instance_folder / "config.cfg"
    # if configFile.is_file():
    #     return False
    
    db_path = instance_folder / "gruenzeit.db"
    
    config_content = [
        f"DEBUG = False",
        f"SECRET_KEY = '{str(token_urlsafe(16))}'",
        f"SQLALCHEMY_DATABASE_URI = 'sqlite:///{db_path}'"
    ]

    os.makedirs(os.path.dirname(instance_folder), exist_ok=True)

    with open(configFile, 'w') as config_file:
        config_file.write("\n".join(config_content))

    print(f"Configuration file created at: {instance_folder}")
    return True


if __name__ == "__main__":
    path = Path(os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "instance"))
    if not generate_config_file(path):
        print("file Already Exists")
