from pathlib import Path
import yaml
import os

__all__ = ("load_config",)


def load_config(config_file=None):
    default_file = Path(__file__).parent / "config.yaml"
    with open(default_file, "r") as f:
        config = yaml.safe_load(f)

    cf_dict = {}
    if config_file:
        cf_dict = yaml.safe_load(config_file)
    if os.environ.get("DB", None):
        config["database_uri"] = os.environ["DB"]
    if cf_dict:
        config.update(**cf_dict)

    return config
