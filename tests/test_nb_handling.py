import pytest

from nb_handling import extract_variable



def test_extract_variable():

    cell = {'cell_type': 'markdown',
   'metadata': {},
   'source': ['## input_variable: df1, df2, df3']}

    assert extract_variable(cell) == ['df1', 'df2', 'df3']