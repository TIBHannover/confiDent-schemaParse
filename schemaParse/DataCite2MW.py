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


def get_documentation(el, doc_xpath: str):
    documentation = ''
    for doc in el.findall(doc_xpath,
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
        el=resource,
        doc_xpath='.//xs:annotation/xs:documentation')

    resource_dict = {resource.get('name'): {
        'name': resource.get('name'),
        'type': _type,
        'kind': 'Entity',
        'cardinality': 1,  # TODO: Philip logic
        'definition': documentation
    }}
    return resource, resource_dict


def get_cardinality(el) -> str:
    minOccurs = el.get('minOccurs')
    maxOccurs = el.get('maxOccurs')
    if minOccurs == "1" and maxOccurs == "1":
        cardinality = "1"  # required, non-repeatable
    elif minOccurs == "1" and maxOccurs == "unbounded":
        cardinality = "1-n"  # required, repeatable
    elif minOccurs == "0" and maxOccurs == "1":
        cardinality = "0-1"  # optional, non-repeatable
    elif minOccurs == "0" and maxOccurs == "unbounded":
        cardinality = "0-n"  # optional, repeatable
    elif maxOccurs == "unbounded":  # absent minOccurs -> default: 1
        cardinality = "1-n"  # required, repeatable
    else:  # absent minOccurs maxOccurs -> default(both): 1
        cardinality = "1"  # required, non-repeatable

    # print(f"min:{minOccurs} max:{maxOccurs}")
    # print(f"cardinality:{cardinality}")
    return cardinality


def get_attribute(attr_el) -> dict:
    attr_name = attr_el.get('name')
    attr_dict = fill_prop_dict(name=attr_name,
                               kind='Attribute',
                               _type=attr_el.get('type'),
                               cardi=attr_el.get('use'),
                               doc="** Attribute needs reviewing**:'use' attr "\
                                   "in cardinality; ")
    attr_dict = {attr_name: attr_dict}
    return attr_dict


def get_subproperty(subprop_el) -> (str, dict):
    sub_prop_name = subprop_el.get('name')
    if subprop_el.find('./xs:complexType/', namespaces=ns) is not None:
        prop_type = 'complexType'
    else:
        prop_type = 'simpleType'

    cardi = get_cardinality(el=subprop_el)

    prop_dict = fill_prop_dict(name=sub_prop_name,
                               _type=prop_type,
                               kind='SubProperty',
                               doc='',  # subProps do not seem to have document.
                               cardi=cardi
                               )
    return sub_prop_name, prop_dict


def get_property(tree, prop_el: str) -> (str, dict):
    '''
    Identifies property attributes:
    * property name
    * complexType OR simpleType
        * complexType: simpleContent sequence or
     sequence OR simpleContent
    Returns (propety_name, prop_dict)

    '''
    prop_el_squnce = None
    if prop_el.find('./xs:complexType/xs:sequence', namespaces=ns) is not None:
        prop_type = 'complexType'
        prop_el_squnce = prop_el.find('./xs:complexType/xs:sequence/xs:element',
                                      namespaces=ns)
        prop_name = prop_el_squnce.get('name')
    elif prop_el.find('./xs:complexType/xs:simpleContent',
                      namespaces=ns) is not None:
        prop_type = 'complexType'
        prop_name = prop_el.get('name')
    elif prop_el.find('./xs:simpleType',
                      namespaces=ns) is not None:
        prop_type = 'simpleType'
        prop_name = prop_el.get('name')
    else:
        # properties language & version have NO complexType or simpleType
        # I will assume they are simpleType ヽ༼ຈل͜ຈ༽ﾉ
        prop_type = 'simpleType'
        prop_name = prop_el.get('name')

    doc = get_documentation(el=prop_el,
                            doc_xpath='.//xs:annotation/xs:documentation')
    if prop_el_squnce is not None:  # element with sequence
        cardi = get_cardinality(el=prop_el_squnce)
    else:
        cardi = get_cardinality(el=prop_el)

    prop_dict = fill_prop_dict(name=prop_name,
                               _type=prop_type,
                               kind='Property',
                               doc=doc,
                               cardi=cardi)
    # pprint(name_type_dict)
    if __debug__ and prop_dict.get('name') not in prop_el.get("name"):
        print('Error: {} is not in {}'.format(
            prop_dict.get('name'),
            prop_el.get("name"))
        )
        raise AssertionError
    return prop_name, prop_dict


def fill_prop_dict(name: str, _type: str = '', kind: str = '', doc: str = '',
                   allowed: str = '', cardi: int = 1, exe: str = '') -> dict:
    prop_dict = {
        'name': name,
        'type': _type,
        'kind': kind,
        'cardinality': cardi,
        'definition': doc,
        'allowedValue': allowed,
        'examples': exe}
    return prop_dict


def parse_prop_n_subp(tree, prop_el) -> dict:
    prop_name, prop_dict = get_property(tree, prop_el)
    prop_n_subprop_dict = {prop_name: prop_dict}
    # sub properties
    subprop_xpath = './xs:complexType/xs:sequence/xs:element/xs' \
                    ':complexType/xs:sequence/xs:element'

    # attributes: both props on subprops can have, hence repeating .findall
    attr_xpath = './xs:complexType/xs:simpleContent/xs:extension/xs:attribute'
    for attr in prop_el.findall(attr_xpath, namespaces=ns):
        attr_dict = get_attribute(attr)
        prop_n_subprop_dict.update(attr_dict)
        # print(etree.tostring(attr))

    if prop_dict['type'] == 'complexType' and \
            prop_el.find(subprop_xpath, namespaces=ns) is not None:
        for sub in prop_el.findall(subprop_xpath, namespaces=ns):
            subprop_name, subprop_vals_dict = get_subproperty(subprop_el=sub)
            subprop_dict = {subprop_name: subprop_vals_dict}
            prop_n_subprop_dict.update(subprop_dict)
            for attr in sub.findall(attr_xpath, namespaces=ns):
                attr_dict = get_attribute(attr)
                prop_n_subprop_dict.update(attr_dict)
                # print(etree.tostring(attr))
    # TODO:
    # * **attribute** needs revewing
    # * HOw to handle <xs:attribute ref="xml:lang"/> attrib for language of
    # content
    # * How to handle attributes without type?
    #
    # * attribute and sub property parent: not present on MW output

    # pprint(prop_n_subprop_dict)
    return prop_n_subprop_dict


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
        prop_dict=parse_prop_n_subp(tree=tree, prop_el=prop)
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