import os
import yaml


def parse_configuration(file_name, config_key):
    """
    Method to parse yaml configuration file.

    Args:
        file_name: name of the config file
        config_key: SceneElementType or str

    Returns:
        Dictionary containing the default configuration of the body part.

    """

    yml_file_name = file_name + '.yml'

    with open(os.path.join(os.path.dirname(__file__), yml_file_name),
              'r') as yaml_file:
        default_config = yaml.load(yaml_file, Loader=yaml.FullLoader)

    if hasattr(config_key, 'name'):
        config_key = config_key.name.lower()

    if config_key not in default_config:
        return {}

    return default_config[config_key]
