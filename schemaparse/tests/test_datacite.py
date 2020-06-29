# import pytest
# import sys, os
# testpath = os.path.dirname(os.path.abspath(__file__))
# sys.path.insert(0, testpath + '/../')
from schemaparse import app


def test_output_mw():
    schema_wiki = app.schema2mw(_schema='DataCite')
    assert len(schema_wiki) > 0

# print(schema_wiki)

# def test_sum():
#     assert sum([1, 2, 3]) == 6, "Should be 6"
#
#
# def test_sum_tuple():
#     assert sum((1, 2, 2)) == 5, "Should be 6"
