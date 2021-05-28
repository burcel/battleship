import yaml


class ConfigParser:
    PATH = "config.yaml"

    def __init__(self):
        self.server_ip = None
        self.server_port = None
        self.read()

    def read(self) -> None:
        """
        Read YAML file and populate variables
        """
        with open(self.PATH, 'r') as file:
            config_dict = yaml.safe_load(file)
            self.server_ip = config_dict["server"]["ip"]
            self.server_port = config_dict["server"]["port"]
