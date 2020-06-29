from schemaparse.utilities import readyaml
from schemaparse.__main__ import schemas as schemas_available


def test_yml():
    for s in schemas_available:
        '''are yaml mappings present and dictionaries?'''
        ext_schema_mapping = readyaml.yaml_get_schemamapping(s)
        assert isinstance(ext_schema_mapping, dict) is True
        '''are the values instnace of str?'''
        for k, v in ext_schema_mapping.items():
            assert isinstance(v, str) and v is not None
        '''Is all necessary schema_info received from yaml file?'''
        uri, ns, ns_prefix, ctype = readyaml.yaml_get_schemainfo(schema=s)
        infolist = [uri, ns, ns_prefix, ctype]
        for i in infolist:
            assert i is not None and isinstance(i, str)
