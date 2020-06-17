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


def property_type(tree, prop_el):
    '''Does this property sequence OR simpleContent this property hold? Ff:
    * simpleContent: get property name from prop_el
    * sequence: get property name get prop_el/complexType/sequence/element

    Sub properties
     *
    '''

    complexType_child = prop_el.find('./xs:complexType/*', namespaces=ns)
    # TODO: understand why publicationYear, language, version do not have
    #  child of ./xs:complexType/
    simple_or_sequence = complexType_child.tag if complexType_child is not \
                                                 None else 'None'
    simple_or_sequence = simple_or_sequence.replace(XMLSchema, "")\
        .replace('{','').replace('}','') # remove ns

    print(f'Parent TAG:{prop_el.get("name")}',
          f'TYPE:{simple_or_sequence}'
          )

    if simple_or_sequence == 'simpleContent':
        prop_name = prop_el.get('name')

    elif simple_or_sequence == 'sequence':
        prop_el_squnce = prop_el.find('./xs:complexType/xs:sequence/xs:element',
                                      namespaces=ns)

    else:
        prop_name = prop_el.get('name')

    if __debug__:
        if prop_name not in prop_el.get("name"):
            print(f'Error: {prop_name} is not in {prop_el.get("name")}')
            raise AssertionError

    print(f'PROPNAME: {prop_name}')
    return prop_name
        # None


def parse_properties(tree, prop_el) -> Dict:
    prop_name = property_type(tree, prop_el)

    for tag in tree.findall('./'):  # direct child elements
        # TODO: review Type
        if 'Type' in tag.tag:
            prop_type = tag.tag
            prop_type = prop_type.replace(f'{{{XMLSchema}}}', '')  # rm schema uri
        else:
            prop_type = ''


    documentation = get_documentation(
        parent_el=prop_el,
        doc_xpath='.//xs:annotation/xs:documentation')

    prop_dict = {prop_el.get('name'): {
        'name': prop_name,
        'type': prop_type,
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