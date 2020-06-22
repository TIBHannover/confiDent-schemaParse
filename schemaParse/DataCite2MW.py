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
ns = {'xs': XMLSchema}

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


def get_documentation(parent_el, doc_xpath: str):
    documentation = ''
    for doc in parent_el.findall(doc_xpath,
                                namespaces=ns):
        documentation += doc.text
    documentation = documentation.replace('\n\n', '')  # remove empty lines
    return documentation


def parse_resource(tree, resource_root_xpath: str) -> (str,Dict):
    resource = tree.find(resource_root_xpath,
                         namespaces=ns)
    for tag in resource.findall('./'):  # direct child elements, no sub-sub els
        if 'Type' in tag.tag:
            _type = tag.tag
            _type = _type.replace(f'{{{XMLSchema}}}', '')  # rm schema uri
    documentation = get_documentation(
        parent_el=resource,
        doc_xpath='.//xs:annotation/xs:documentation')

    resource_dict = {resource.get('name'): {
        'name': resource.get('name'),
        'type': _type,
        'kind': 'Entity',
        'cardinality': 1,  # TODO: Philip logic
        'definition': documentation
    }}
    return resource, resource_dict


def property_nameNtype(tree, prop_el) -> dict:
    '''
    Identifies property attributes:
    * property name
    * complexType OR simpleType
        * complexType: simpleContent sequence or
     sequence OR simpleContent
    Returns dict:
        prop: {
        name:
        type: complexType OR simpleType,
        complexType: simpleContent or sequence or (None for simpleType)
                        }
    '''

    if prop_el.find('./xs:complexType/xs:sequence', namespaces=ns) is not None:
        prop_type = 'complexType'
        prop_complexType = 'sequence'
        prop_el_squnce = prop_el.find('./xs:complexType/xs:sequence/xs:element',
                                      namespaces=ns)
        prop_name = prop_el_squnce.get('name')
    elif prop_el.find('./xs:complexType/xs:simpleContent',
                      namespaces=ns) is not None:
        prop_type = 'complexType'
        prop_complexType = 'simpleContent'
        prop_name = prop_el.get('name')
    elif prop_el.find('./xs:simpleType',
                      namespaces=ns) is not None:
        prop_type = 'simpleType'
        prop_complexType = None
        prop_name = prop_el.get('name')
    else:
        # properties language & version have NO complexType or simpleType
        # I will assume they are simpleType ヽ༼ຈل͜ຈ༽ﾉ
        prop_type = 'simpleType'
        prop_complexType = None
        prop_name = prop_el.get('name')

    nameNtype_dict = {'type': prop_type,
                 'complexType': prop_complexType,
                 'name': prop_name
                }
    pprint(nameNtype_dict)
    if __debug__:
        if nameNtype_dict.get('name') not in prop_el.get("name"):
            print('Error: {} is not in {}'.format(
                nameNtype_dict.get('name'),
                prop_el.get("name"))
            )
            raise AssertionError
    return nameNtype_dict


    # # REUSE THIS IN SEQUENCE SUB ELEMENTs
    # elif simple_or_sequence == 'sequence':
    #     prop_el_squnce = prop_el.find('./xs:complexType/xs:sequence/xs:element',
    #                                   namespaces=ns)
    #     prop_name = prop_el_squnce.get('name')
    #     sub_properties = prop_el_squnce.findall(
    #         './xs:complexType/xs:sequence/xs:element', namespaces=ns)
    #     for sub in sub_properties:
    #         sub_prop_name = sub.get('name')
    #         print(f'SUB {sub_prop_name}')

def parse_properties(tree, prop_el) -> Dict:
    nameNtype_dict = property_nameNtype(tree, prop_el)

    # for tag in tree.findall('./'):  # direct child elements
    #     # TODO: review Type
    #     if 'Type' in tag.tag:
    #         prop_type = tag.tag
    #         prop_type = prop_type.replace(f'{{{XMLSchema}}}', '')  # rm schema uri
    #     else:
    #         prop_type = ''

    documentation = get_documentation(
        parent_el=prop_el,
        doc_xpath='.//xs:annotation/xs:documentation')

    prop_dict = {prop_el.get('name'): {
        'name': nameNtype_dict['name'],
        'type': nameNtype_dict['type'],
        'kind': 'Property',
        'cardinality': 1, # TODO: Philip logic
        'definition': documentation,
        'allowedValue': '',
        'examples': ''}}
    return prop_dict


def dataciteSchema2dict(xmlcode: str) -> Dict:
    datacite_els_dict = OrderedDict()
    tree = etree.fromstring(xmlcode)

    ## if reading fromfile, use:
    # tree = etree.parse(xml_file_path)
    # root = tree.getroot()
    # & replace tree-> root

    # resource (entity)
    resource, resource_dict = parse_resource(
        tree=tree,
        resource_root_xpath='.//xs:element[@name="resource"]'
    )
    datacite_els_dict.update(resource_dict)

    # properties
    for prop in resource.findall('./xs:complexType/xs:all/xs:element',
                                  namespaces=ns):
        prop_dict= parse_properties(tree=tree, prop_el=prop)
        datacite_els_dict.update(prop_dict)

    return datacite_els_dict


schema_xml = fetch_schema(uri=datacite_schema_uri,
                          contenttype='application/rdf+xml')

datacite_elements = dataciteSchema2dict(xmlcode=schema_xml)
# print(datacite_elements.keys())
# pprint(datacite_elements)

datacite_smw = datacite_properties_template.render(
    elements_dict=datacite_elements
)

print(datacite_smw)