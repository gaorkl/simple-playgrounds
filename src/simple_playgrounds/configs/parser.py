from __future__ import annotations

from typing import Union, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..common.definitions import ElementTypes, SensorTypes
    from simple_playgrounds.agents.parts import PartTypes

import os
import yaml


def parse_configuration(
    file_name: str,
    config_key: Optional[Union[PartTypes, ElementTypes, SensorTypes,
                               str]] = None,
):
    """
    Method to parse yaml configuration file.

    Args:
        file_name: name of the config file
        config_key: PartTypes, ElementTypes or str

    Returns:
        Dictionary containing the default configuration of the body part.

    """

    yml_file_name = file_name + '.yml'

    with open(os.path.join(os.path.dirname(__file__), yml_file_name),
              'r') as yaml_file:
        default_config = yaml.load(yaml_file, Loader=yaml.FullLoader)

    # Hacky but there are circular dependencies
    if hasattr(config_key, 'name'):
        key_name = config_key.name.lower()  # type: ignore

    elif isinstance(config_key, str):
        key_name = config_key

    else:
        key_name = None

    return default_config.get(key_name, {})
