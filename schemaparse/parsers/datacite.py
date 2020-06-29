from typing import Dict
from _collections import OrderedDict
from lxml import etree
import schemaparse.globals as _globals


def get_documentation(el, doc_xpath: str):
    documentation = ''
    for doc in el.findall(doc_xpath,
                          namespaces=_globals.schemainfo.ns_dict):
        documentation += doc.text
    documentation = documentation.replace('\n\n', '')  # remove empty lines
    return documentation


def add_parent(nodedict: Dict, parentname: str):
    # adds parent key to schema note dictionary
    key = (list(nodedict.keys()))[0]
    nodedict[key]['parent'] = parentname


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
    # TODO: expand:
    attr_name = attr_el.get('name')
    attr_dict = fill_prop_dict(name=attr_name,
                               kind='Attribute',
                               _type=attr_el.get('type'),
                               cardi=attr_el.get('use'),
                               doc="** Attribute needs reviewing**:'use' "
                                   "attr in cardinality; ")
    attr_dict = {attr_name: attr_dict}
    return attr_dict


def get_subproperty(subprop_el) -> dict:
    sub_prop_name = subprop_el.get('name')
    if subprop_el.find('./xs:complexType/',
                       namespaces=_globals.schemainfo.ns_dict) is not None:
        prop_type = 'complexType'
    else:
        prop_type = 'simpleType'
    cardi = get_cardinality(el=subprop_el)
    prop_dict = fill_prop_dict(name=sub_prop_name,
                               _type=prop_type,
                               kind='SubProperty',
                               doc='',  # subProps do not seem to have document
                               cardi=cardi)
    prop_dict = {sub_prop_name: prop_dict}
    return prop_dict


def get_property(prop_el: str) -> (str, dict):
    '''
    Identifies property:
    * property name
    * complexType OR simpleType
        * complexType: simpleContent sequence or
     sequence OR simpleContent
    Returns (propety_name, prop_dict)
    '''
    prop_el_sqnce = None
    if prop_el.find('./xs:complexType/xs:sequence',
                    namespaces=_globals.schemainfo.ns_dict) is not None:
        prop_type = 'complexType'
        prop_el_sqnce = prop_el.find('./xs:complexType/xs:sequence/xs:element',
                                     namespaces=_globals.schemainfo.ns_dict)
        prop_name = prop_el_sqnce.get('name')
    elif prop_el.find('./xs:complexType/xs:simpleContent',
                      namespaces=_globals.schemainfo.ns_dict) is not None:
        prop_type = 'complexType'
        prop_name = prop_el.get('name')
    elif prop_el.find('./xs:simpleType',
                      namespaces=_globals.schemainfo.ns_dict) is not None:
        prop_type = 'simpleType'
        prop_name = prop_el.get('name')
    else:
        # properties language & version have NO complexType or simpleType
        # I will assume they are simpleType ヽ༼ຈل͜ຈ༽ﾉ
        prop_type = 'simpleType'
        prop_name = prop_el.get('name')

    doc = get_documentation(el=prop_el,
                            doc_xpath='.//xs:annotation/xs:documentation')
    if prop_el_sqnce is not None:  # element with sequence
        cardi = get_cardinality(el=prop_el_sqnce)
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
    prop_dict = {prop_name: prop_dict}  # prop_dict: {prop_name: {name:...}}
    return prop_name, prop_dict


def parse_resource(tree, resource_root_xpath: str) -> (str, Dict):
    resource = tree.find(resource_root_xpath,
                         namespaces=_globals.schemainfo.ns_dict)
    for tag in resource.findall('./'):  # direct child elements, no sub-sub els
        if 'Type' in tag.tag:
            _type = tag.tag
            _type = _type.replace(f'{{{_globals.schemainfo.ns}}}', '')  # rm ns
    documentation = get_documentation(
        el=resource,
        doc_xpath='.//xs:annotation/xs:documentation')

    resource_dict = {resource.get('name'): {
        'name': resource.get('name'),
        'type': _type,
        'kind': 'Entity',
        'cardinality': 1,
        'definition': documentation
    }}
    return resource, resource_dict


def fill_prop_dict(name: str, _type: str = '', kind: str = '', doc: str = '',
                   allowed: str = '', cardi: str = '', exe: str = '') -> dict:
    prop_dict = {
        'name': name,
        'type': _type,
        'kind': kind,
        'cardinality': cardi,
        'definition': doc,
        'allowedValue': allowed,
        'examples': exe}
    return prop_dict


def parse_property(tree, prop_el) -> dict:
    # def parses 1 property and its descendants: subProperty, attribute
    prop_name, prop_n_subprop_dict = get_property(prop_el)

    # attributes: both props on subprops can have, hence repeating .findall
    attr_xpath = './xs:complexType/xs:simpleContent/xs:extension/xs:attribute'
    for attr in prop_el.findall(attr_xpath,
                                namespaces=_globals.schemainfo.ns_dict):
        attr_dict = get_attribute(attr)
        add_parent(nodedict=attr_dict, parentname=prop_name)
        prop_n_subprop_dict.update(attr_dict)
        # print(etree.tostring(attr))

    # sub properties
    subprop_xpath = './xs:complexType/xs:sequence/xs:element/xs' \
                    ':complexType/xs:sequence/xs:element'
    if prop_n_subprop_dict[prop_name]['type'] == 'complexType' and \
            prop_el.find(subprop_xpath,
                         namespaces=_globals.schemainfo.ns_dict) is not None:
        for sub in prop_el.findall(subprop_xpath,
                                   namespaces=_globals.schemainfo.ns_dict):
            subprop_dict = get_subproperty(subprop_el=sub)
            add_parent(nodedict=subprop_dict, parentname=prop_name)
            prop_n_subprop_dict.update(subprop_dict)
            for attr in sub.findall(attr_xpath,
                                    namespaces=_globals.schemainfo.ns_dict):
                attr_dict = get_attribute(attr)
                add_parent(nodedict=attr_dict,
                           parentname=subprop_dict.get('name'))
                prop_n_subprop_dict.update(attr_dict)
                # print(etree.tostring(attr))
    # pprint(prop_n_subprop_dict)
    return prop_n_subprop_dict


def schema2dict(xmlcode: str) -> Dict:
    elements_dict = OrderedDict()
    tree = etree.fromstring(xmlcode)
    ns_dict = {_globals.schemainfo.ns_prefix: _globals.schemainfo.ns}
    _globals.schemainfo.ns_dict = ns_dict
    # resource (entity)
    resource, resource_dict = parse_resource(
        tree=tree,
        resource_root_xpath='.//xs:element[@name="resource"]'
    )
    elements_dict.update(resource_dict)
    # pprint(elements_dict)

    # properties
    for prop in resource.findall('./xs:complexType/xs:all/xs:element',
                                 namespaces=_globals.schemainfo.ns_dict):
        prop_dict = parse_property(tree=tree, prop_el=prop)
        elements_dict.update(prop_dict)
    return elements_dict
