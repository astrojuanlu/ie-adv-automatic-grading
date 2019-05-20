import numpy as np
import pytest
from ie_pandas import DataFrame


@pytest.fixture
def int_df():
    return DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})


@pytest.fixture
def mixed_df():
    return DataFrame({
        "a": [1, 2, 3],
        "b": [4.0, 5.0, 6.0],
        "c": [True, True, False],
        "d": [".", "..", "..."],
    })


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


def test_edit_col(int_df):
    new_row = np.array([11, 12, 13])

    int_df["a"] = new_row

    assert (int_df["a"] == new_row).all()


def test_edit_col_alt(int_df):
    new_row = [11, 12, 13]

    int_df["a"] = new_row

    assert (int_df["a"] == new_row).all()


def test_types(mixed_df):
    assert mixed_df["a"].dtype == int
    assert mixed_df["b"].dtype == float
    assert mixed_df["c"].dtype == bool
    assert mixed_df["d"].dtype == np.dtype("<U3")


def test_ops(mixed_df):
    assert mixed_df.sum() == [6, 15.0]
    assert mixed_df.median() == [2.0, 5.0]
    assert mixed_df.min() == [1, 4.0]
    assert mixed_df.max() == [3, 6.0]
