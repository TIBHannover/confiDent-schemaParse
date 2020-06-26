from typing import List, Dict, Tuple
import yaml


def yaml2dict(path:str) -> Dict:
    with open(path, 'r') as yaml_f:
        yaml_content = yaml_f.read()
        yaml_dict = yaml.safe_load(yaml_content)
    return yaml_dict


def yaml_get_schemainfo(schema: str) -> Tuple[str, str, str, str]:
    schema_info = yaml2dict('schemaparse/schemas/schemas.yml')
    uri = schema_info[schema]['uri']
    ns = schema_info[schema]['ns']
    ns_prefix = schema_info[schema]['ns_prefix']
    contenttype = schema_info[schema]['contenttype']
    return uri, ns, ns_prefix, contenttype


def yaml_get_schemamapping(schema: str) -> Dict:
    path = f'schemaparse/mappings2confiDent/{schema}.yml'
    confid2ext_schema = yaml2dict(path)
    ext_schema = list(confid2ext_schema.keys())[0]
    ext_schema_mapping = confid2ext_schema[ext_schema]
    return ext_schema_mapping


def prop_extschema2confid(extschema: Dict, extprop: str) -> List[str]:
    '''
    Looks up the external schema dictionary by its value
    So that confiDent property (k) can be found based on external schema's
    propoerty (v)
    :yield: confiDent property mapped to ext schema property
    '''
    for k, v in extschema.items():
        if extprop is not None and v.lower() == extprop.lower():
            yield k


def add_mapsto(mapping: Dict, schema_els: Dict):
    '''
    updates external schema Dict by adding mapsTo key and value (list)
    '''
    for prop_k, prop_dict in schema_els.items():
        prop_name = prop_dict.get('name')
        mapsTo_val = [map_prop for map_prop in prop_extschema2confid(
            extschema=mapping,extprop=prop_name)]
        schema_els[prop_name]['mapsTo'] = mapsTo_val


if __name__ == '__main__':
    extschema, extschema_dict = readmapping_yaml('mappings2confiDent/DataCite.yml')
    # what keys have the value: Title?
    for conf_prop in prop_extschema2confid(extschema=extschema_dict,
                                           extprop='Title'):
        print(conf_prop)
