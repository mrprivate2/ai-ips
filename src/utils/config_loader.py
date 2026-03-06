import yaml


def load_config(path: str):
    """
    Load YAML configuration file.
    """
    with open(path, "r") as file:
        return yaml.safe_load(file)