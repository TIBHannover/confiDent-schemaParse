from typing import Dict, List
from _collections import OrderedDict
from lxml import etree


def get_documentation(el, doc_xpath: str):
    documentation = ''
    for doc in el.findall(doc_xpath,
                          namespaces=ns):
        documentation += doc.text
    documentation = documentation.replace('\n\n', '')  # remove empty lines
    return documentation


def parse_resource(tree, resource_root_xpath: str, ns_schema: str,
                   schema_info: Dict, ns=Dict) -> (str, Dict):
    resource = tree.find(resource_root_xpath,
                         namespaces=ns)
    for tag in resource.findall('./'):  # direct child elements, no sub-sub els
        if 'Type' in tag.tag:
            _type = tag.tag
            _type = _type.replace(f'{{{ns_schema}}}', '')  # rm schema uri
    documentation = get_documentation(
        el=resource,
        doc_xpath='.//xs:annotation/xs:documentation')

    # TODO: resource_dict can it become a common resource ?
    resource_dict = {resource.get('name'): {
        'name': resource.get('name'),
        'type': _type,
        'kind': 'Entity',
        'cardinality': 1,
        'definition': documentation
    }}
    return resource, resource_dict


def schema2dict(xmlcode: str, schema_info: Dict) -> Dict:
    elements_dict = OrderedDict()
    tree = etree.fromstring(xmlcode)
    ns = {schema_info['ns_prefix']: schema_info['ns']}

    # # resource (entity)
    # resource, resource_dict = parse_resource(
    #     tree=tree,
    #     resource_root_xpath='.//xs:element[@name="resource"]',
    #     schema_info=schema_info,
    #     ns=ns
    # )
    # elements_dict.update(resource_dict)
    #
    # # properties
    # for prop in resource.findall('./xs:complexType/xs:all/xs:element',
    #                               namespaces=ns):
    #     prop_dict=parse_property(tree=tree, prop_el=prop)
    #     elements_dict.update(prop_dict)
    #
    # return elements_dict
