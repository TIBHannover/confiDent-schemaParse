from pathlib import Path
import urllib.request
from lxml import etree
from pprint import pprint
from typing import Dict
from collections import OrderedDict
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


def parse_resource(tree, resource_root_xpath: str, ns: dict) -> (str,Dict):
    resource = tree.find(resource_root_xpath,
                         namespaces=ns)
    for tag in resource.findall('./'):  # direct child elements, no sub-sub els
        if 'Type' in tag.tag:
            _type = tag.tag
            _type = _type.replace(f'{{{XMLSchema}}}', '')  # rm schema uri
    documentation = ''
    for doc in resource.findall('.//xs:annotation/xs:documentation',
                                namespaces=ns):
        documentation += doc.text
    documentation = documentation.replace('\n\n', '')  # remove empty lines
    resource_dict = {resource.get('name'): {
        'name': resource.get('name'),
        'type': _type,
        'kind': 'Entity',
        'cardinality': 1,  # TODO: Philip logic
        'definition': documentation
    }}
    return resource, resource_dict

def dataciteSchema2dict(xmlcode: str, xs_uri: str) -> Dict:
    datacite_els_dict = OrderedDict()
    tree = etree.fromstring(xmlcode)

    ## if reading fromfile, use:
    # tree = etree.parse(xml_file_path)
    # root = tree.getroot()
    # & replace tree-> root

    # resource (entity)
    resource, resource_dict = parse_resource(
        tree=tree,
        resource_root_xpath='.//xs:element[@name="resource"]',
        ns={'xs': xs_uri}
    )
    datacite_els_dict.update(resource_dict)

    # properties
    for prop in resource.findall('./xs:complexType/xs:all/xs:element',
                                  namespaces={'xs': xs_uri}):
        for tag in resource.findall('./'):  # direct child elements
            if 'Type' in tag.tag:
                prop_type = tag.tag
                prop_type = prop_type.replace(f'{{{XMLSchema}}}', '')  # rm schema uri

        # prop name: if plural seek single element
        #   note that filtering according to .endswith('s') is failable
        #   but seems to work for DataCite
        # TODO TEST: all properies have "|name=" value
        if prop.get('name').endswith('s'):
            prop_single = prop.find('./xs:complexType/xs:sequence/xs:element',
                                    namespaces={'xs': xs_uri})
            prop_name = prop_single.get('name')
        else:
            prop_name = prop.get('name')

        documentation = ''
        for doc in prop.findall('.//xs:annotation/xs:documentation',
                              namespaces={'xs': xs_uri}):
            documentation += doc.text
        documentation = documentation.replace('\n\n', '') # remove empty lines

        datacite_els_dict[prop.get('name')] = {
            'name': prop_name,
            'type': prop_type,
            'kind': 'Property',
            'cardinality': 1, # TODO: Philip logic
            'definition': documentation,
            'allowedValue': '',
            'examples': ''
    }
    return datacite_els_dict


schema_xml = fetch_schema(uri=datacite_schema_uri,
                          contenttype='application/rdf+xml')

datacite_elements = dataciteSchema2dict(xmlcode=schema_xml, xs_uri=XMLSchema)
# print(datacite_elements.keys())
# pprint(datacite_elements)

datacite_smw = datacite_properties_template.render(
    elements_dict=datacite_elements
)

print(datacite_smw)