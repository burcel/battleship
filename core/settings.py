from typing import Optional

import yaml


class Settings:
    PATH = "config.yaml"

    def __init__(self):
        """ Read YAML file and populate variables """
        with open(self.PATH, 'r') as file:
            config_dict = yaml.safe_load(file)
            self.name: str = config_dict["name"]
            self.server_ip: str = config_dict["server"]["ip"]
            self.server_port: int = config_dict["server"]["port"]
            self.token_expire_min: int = config_dict["server"]["token_expire_min"]
            self.database_url: str = config_dict["database"]["url"]


settings = Settings()
