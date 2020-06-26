from typing import Dict, List
from urllib import request
from schemaparse.parsers import datacite
from schemaparse import app
import schemaparse.globals as _globals


def fetch_schema(uri: str, contenttype: str) -> str:
    request_headers = {'Accept': contenttype}
    request_url = request.Request(uri, headers=request_headers)
    response = request.urlopen(request_url)
    data = response.read()
    return data


def parseschema(template: object):
    schema_xml = fetch_schema(uri=_globals.schemainfo.uri,
                              contenttype=_globals.schemainfo.contenttype)
    if _globals.schemainfo.schema == 'DataCite':
        schema_dict = datacite.schema2dict(xmlcode=schema_xml)


