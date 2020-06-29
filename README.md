# Parse schemas and integrate onto SMW

# current schemas:
* [Datacide](https://schema.datacite.org/meta/kernel-4.3/) (work in progress)

## install requirements

`pip install -r requirements.txt`

## run
* `python -m schemaparse` (default DataCite)
* `python -m schemaparse --list` available schemas
* `python -m schemaparse --help`

## debug

With iPython / Python and module import:
```python
from pprint import pprint
from schemaparse.utilities import readyaml
mapping_dict = readyaml.yaml_get_schemamapping(schema='DataCite')
pprint(mapping_dict)

{'EventDuration': 'PublicationYear',
 'EventId': 'Identifier',
 'EventName': 'Title',
 'SeriesId': 'Identifier',
 'SeriesName': 'Title'}
```

## TODO
* mapping needs to be handled outside the datacide module
    
# Application structure
* `app.py`
* `mappings2confiDent/` - yaml files mapping confiDent properties to other schemas 
* `parsers/` - python modules for parsing schemas
* `schemas/` - yaml files with info on the schema: URI, NS
* `templates/` - Jinja templates for outputting parsing results from dictionary to plain text 
* `utilities/` - utility python modules
* `__main__.py`