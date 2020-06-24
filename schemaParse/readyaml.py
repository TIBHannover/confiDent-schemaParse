from typing import List, Dict
import yaml


def readmapping_yaml(path:str) -> (str, Dict):
    with open('mappings2confiDent/DataCite.yml', 'r') as ext_schemayml_f:
        ext_schemayml = ext_schemayml_f.read()
        confiD2ext_schema = yaml.safe_load(ext_schemayml)
    ext_schema = list(confiD2ext_schema.keys())[0]
    ext_schema_mapping = confiD2ext_schema[ext_schema]
    return ext_schema, ext_schema_mapping


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
