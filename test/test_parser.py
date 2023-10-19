import pytest


@pytest.mark.parametrize(
    "test, expected, expect_raises",
    [(f"parser_tests_jsons/test_{test_number}.json", None, ValueError) for test_number in range(1, 9)])
def test_parser_for_errors(test, expected, expect_raises):
    """Test mean function works for array of zeroes and positive integers."""
    from system_parser import Parser
    with pytest.raises(expect_raises):
        assert Parser(test).construct() == expected


expected_values = [[{'subcutaneous': 0, 'dose': [20, 'continuous']}, [
    {'name': 'bloodstream', 'type': 'central', 'volume': 5000, 'initial_amount': 0.0,
     'rate_out': 1.0, 'rate_in': None},
    {'name': 'adipose', 'type': 'peripheral', 'volume': 1.0, 'initial_amount': 0.0,
     'rate_in': 1.0, 'rate_out': 1.0}]],
                   [{'subcutaneous': 0, 'dose': [2, 'continuous']}, [
                       {'name': 'bloodstream', 'type': 'central', 'volume': 5000, 'initial_amount': 0.0,
                        'rate_out': 1.0, 'rate_in': None},
                       {'name': 'adipose', 'type': 'peripheral', 'volume': 1.0, 'initial_amount': 0.0, 'rate_in': 1.0,
                        'rate_out': 1.0},
                       {'name': 'adipose', 'type': 'peripheral', 'volume': 3000, 'initial_amount': 0.0, 'rate_in': 1.0,
                        'rate_out': 3}]]]


@pytest.mark.parametrize(
    "test, expected",
    [(f"parser_tests_jsons/test_9.json", expected_values[0]),
     (f"parser_tests_jsons/test_10.json", expected_values[1])])
def test_parser_for_wrong_output(test, expected):
    from system_parser import Parser
    assert Parser(test).construct() == expected
