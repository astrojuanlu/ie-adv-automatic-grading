import numpy as np
import pytest
from ie_pandas import DataFrame


@pytest.fixture
def int_df():
    return DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})


def test_creation():
    DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    DataFrame({"a": np.array([1, 2, 3]), "b": np.array([4, 5, 6])})


@pytest.mark.parametrize(
    "index, expected_result", [[0, [1, 4]], [1, [2, 5]], [2, [3, 6]]]
)
def test_get_row(index, expected_result, int_df):
    result = int_df.get_row(index)

    assert result == expected_result


@pytest.mark.parametrize(
    "col, expected_result", [["a", np.array([1, 2, 3])], ["b", np.array([4, 5, 6])]]
)
def test_get_col(col, expected_result, int_df):
    result = int_df[col]

    assert (result == expected_result).all()
