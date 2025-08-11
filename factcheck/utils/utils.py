import yaml
import os


def load_yaml(filepath):
    with open(filepath, "r") as file:
        config = yaml.safe_load(file)
    
    # Iterate through the config and replace values with environment variables
    for key, value in config.items():
        if isinstance(value, str):
            config[key] = os.environ.get(value, None)
            
    return config
