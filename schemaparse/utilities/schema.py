from typing import Dict
from urllib import request
from schemaparse.parsers import datacite
from schemaparse.utilities import readyaml
import schemaparse.globals as _globals


def fetch_schema(uri: str, contenttype: str) -> str:
    request_headers = {'Accept': contenttype}
    request_url = request.Request(uri, headers=request_headers)
    response = request.urlopen(request_url)
    data = response.read()
    return data


def parseschema(template: object, mapping: Dict) -> Dict:
    schema_xml = fetch_schema(uri=_globals.schemainfo.uri,
                              contenttype=_globals.schemainfo.contenttype)
    if _globals.schemainfo.schema == 'DataCite':
        schema_dict = datacite.schema2dict(xmlcode=schema_xml)

    readyaml.add_mapsto(mapping=mapping, schema_els=schema_dict)
    schema_smw = template.render(elements_dict=schema_dict)
    # pprint(schema_dict)  # uncomment to debug
    return schema_smw
