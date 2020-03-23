import os, yaml

def get_yaml_config( filename, key=None ):

    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    with open(os.path.join(__location__, filename), 'r') as yaml_file:
        if key is None:
            default_config = yaml.load(yaml_file)
        else:
            default_config = yaml.load(yaml_file)[key]

    return default_config