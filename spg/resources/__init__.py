from pathlib import Path

from arcade.resources import add_resource_handle

#: The absolute path to this directory
SPG_RESOURCE_PATH = Path(__file__).parent.resolve()

add_resource_handle("spg", SPG_RESOURCE_PATH)
