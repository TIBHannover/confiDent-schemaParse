from typing import Dict, List
from urllib import request
from schemaparse.parsers import datacite


def fetch_schema(uri: str, contenttype: str) -> str:
    request_headers = {'Accept': contenttype}
    request_url = request.Request(uri, headers=request_headers)
    response = request.urlopen(request_url)
    data = response.read()
    return data


def parseschema(schema_info: Dict, template: object):
    schema_xml = fetch_schema(uri=schema_info['uri'],
                              contenttype=schema_info['contenttype'])
    if schema_info['schema'] == 'DataCite':
        schema_dict = datacite.schema2dict(xmlcode=schema_xml,
                                           schema_info=schema_info)


