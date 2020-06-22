
 # DONE
* properties: query single and not
    ie.  <xs:element name="creator" maxOccurs="unbounded">
        and not <xs:element name="creators">

# TODO:
* SubProperty
* attribute -> descendent of  element of
* cardinality:
* mapsTo
* type: needs clarification
* allowedValue (for later)
* example (for later)

# Notes
## on Destinguishing between properties and sub properties

property w/out sub properties
* identifier:
    * `element/complexType/simpleContent/extension/`
    * `/xs:schema/xs:element/xs:complexType/xs:all/xs:element[1]/xs:complexType/xs:simpleContent/xs:extension`

* property w sub-property: ie.creators:
    * `element/complexType/sequence/element/complexType/ simpleContent`
    * `/xs:schema/xs:element/xs:complexType/xs:all/xs:element[2]/xs:complexType/xs:sequence/xs:element/xs:complexType/xs:sequence/xs:element[1]`
    * `/xs:schema/xs:element/xs:complexType/xs:all/xs:element[2]/xs:complexType/xs:sequence/xs:element/xs:complexType/xs:sequence/xs:element[2]/@name`

property:
* `/xs:schema/xs:element/xs:complexType/xs:all/xs:element[2]/xs:complexType/xs:sequence/xs:element/`

subproperties:
* `/xs:schema/xs:element/xs:complexType/xs:all/xs:element[2]/xs:complexType/xs:sequence/xs:element/xs:complexType/xs:sequence/xs:element`


```
{{SchemaProperty
|id=DataCite::identifier
|name=Identifier
|kind=Property  ---> infer kind form nesting levet :////
|type=XSD:complexType --> tag name
|parent=     --> ???? (save for later)
|cardinality=1   ->> 1  .. needs clarification
      minOccurs="0" maxOccurs="unbounded"

|mapsTo=ConfIDentSchema/EventId
    TODO: schema mapping through YAML file.
    TODO: Phillip will do a dictionary mapping

|definition=A persistent identifier that identifies a resource.
            Documentation
|allowedValue=DOI (Digital Object Identifier) registered by a DataCite member. Format should be “10.1234/foo”
    keep empty for now
|examples=10.1234/foo
    keep empty for now
|schema=DataCite
|storemode=subobject
    Forms templates related (keep as is)
}}


```
