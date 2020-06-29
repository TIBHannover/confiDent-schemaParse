from schemaparse import app


def test_output_mw():
    schema_wiki = app.schema2mw(_schema='DataCite')
    assert len(schema_wiki) > 0


'''
What tests can we write?
* (todo) are the amount of wiki template instances the same as dictionary keys?

'''
