# Parse schemas and integrate onto SMW

# current schemas:
* [Datacide](https://schema.datacite.org/meta/kernel-4.3/) (work in progress)

## install requirements

`pip install -r requirements.txt`

## run
* `python -m schemaparse` (default DataCite)
* `python -m schemaparse --list` available schemas
* `python -m schemaparse --help`

## TODO
* make template more general purpose 
    * How similar in DC MW template to other Schemas templates?
    * no need to have Datacite hardcoded