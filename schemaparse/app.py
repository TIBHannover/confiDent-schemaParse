from typing import Tuple
from pathlib import Path
from jinja2 import (FileSystemLoader,
                    Environment)
from schemaparse.utilities import readyaml


# extschema, extschema_mapping = readmapping_yaml('mappings2confiDent/DataCite.yml')


def load_template(schema: str):
    # Jinja: Env & Templates
    project_dir = Path(__file__).parent.absolute()
    f_loader = FileSystemLoader(project_dir / 'templates')
    env = Environment(loader=f_loader)
    template = env.get_template(f'{schema}_properties.jinja')
    return template


def schema2mw(schema):
    s = f'Schema {schema} will be turned to MW'
    template = load_template(schema)
    uri, ns, ns_prefix = readyaml.yaml_get_schemainfo(schema)
    mapping = readyaml.yaml_get_schemamapping(schema)

    print(uri, ns, ns_prefix)
    print(mapping)

    return(s)