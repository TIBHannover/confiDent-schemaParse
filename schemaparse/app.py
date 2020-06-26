from pathlib import Path
from jinja2 import (FileSystemLoader,
                    Environment)
from schemaparse.utilities import readyaml
from schemaparse.utilities import schema
import schemaparse.globals as _globals


class SchemaInfo:
    def __init__(self, schemaname: str, uri: str, ns: str, ns_prefix: str,
                 contenttype: str):
        self.schema = schemaname
        self.uri = uri
        self.ns = ns
        self.ns_prefix = ns_prefix
        self.contenttype = contenttype


def load_template(schema: str):
    # Jinja: Env & Templates
    project_dir = Path(__file__).parent.absolute()
    f_loader = FileSystemLoader(project_dir / 'templates')
    env = Environment(loader=f_loader)
    template = env.get_template(f'{schema}_properties.jinja')
    return template


def schema2mw(_schema):
    s = f'Schema {_schema} will be turned to MW'
    template = load_template(_schema)
    uri, ns, ns_prefix, contenttype = readyaml.yaml_get_schemainfo(_schema)
    mapping = readyaml.yaml_get_schemamapping(_schema)
    _globals.schemainfo = SchemaInfo(schemaname=_schema,
                                     uri=uri,
                                     ns=ns,
                                     ns_prefix=ns_prefix,
                                     contenttype=contenttype)
    schema.parseschema(template=template)

    print(template, uri, ns, ns_prefix)
    print(mapping)
    print(_globals.schemainfo.__dict__)
    return(s)
