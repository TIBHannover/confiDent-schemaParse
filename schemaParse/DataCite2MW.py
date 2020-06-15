from pathlib import Path
import urllib.request
from lxml import etree
from pprint import pprint
from typing import Dict
from jinja2 import (FileSystemLoader,
                    Environment)

datacite_schema_uri = 'https://schema.datacite.org/meta/kernel-4.3/metadata.xsd'
XMLSchema = 'http://www.w3.org/2001/XMLSchema'

# Jinja: Env & Templates
project_dir = Path(__file__).parent.absolute()
f_loader = FileSystemLoader(project_dir / 'templates')
env = Environment(loader=f_loader)
datacite_properties_template = env.get_template('DataCite_properties.jinja')



def fetch_schema(uri: str, contenttype: str) -> str:
    request_headers = {'Accept': contenttype}
    request = urllib.request.Request(uri, headers=request_headers)
    response = urllib.request.urlopen(request)
    data = response.read()
    return data


def dataciteSchema2dict(xmlcode: str, xs_uri: str) -> Dict:
    datacite_els_dict = {}
    tree = etree.fromstring(xmlcode)

    ## if reading fromfile, use:
    # tree = etree.parse(xml_file_path)
    # root = tree.getroot()
    # & replace tree-> root

    # element(s) of  <xs:element name="resource">
    resource = tree.find('.//xs:element[@name="resource"]',
                         namespaces={'xs': xs_uri})

    for el in resource.findall('./xs:complexType/xs:all/xs:element',
                               namespaces={'xs': xs_uri}):

        # ... should try to gather more info about each element/property

        documentation = ''
        for doc in el.findall('.//xs:annotation/xs:documentation',
                              namespaces={'xs': xs_uri}):
            documentation += doc.text
        datacite_els_dict[el.get('name')] = {'documentation': documentation}
    return datacite_els_dict


schema_xml = fetch_schema(uri=datacite_schema_uri,
                          contenttype='application/rdf+xml')

datacite_elements = dataciteSchema2dict(xmlcode=schema_xml, xs_uri=XMLSchema)
# print(datacite_elements.keys())
pprint(datacite_elements)

datacite_smw = datacite_properties_template.render(
    elements_dict=datacite_elements)
datacite_smw = datacite_smw.replace('\n\n', '') # remove empty lines
print(datacite_smw)