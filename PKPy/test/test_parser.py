"""
This module contains unit tests for the Parser class in the system_parser module.
The tests include:
- test_parser_for_errors: tests if the Parser class raises the expected errors for a range of test cases.
- test_parser_for_wrong_output: tests if the Parser class returns the expected output for a range of test cases.
"""
import pytest

@pytest.mark.parametrize(
    "test, expected, expect_raises",
    [(f"PKPy/test/parser_tests_jsons/test_{test_number}.json", None, ValueError) for test_number in range(1, 9)])
def test_parser_for_errors(test, expected, expect_raises):
    """
    Test the Parser class for expected errors.

    :param test: The input string to be parsed.
    :type test: str
    :param expected: The expected output string.
    :type expected: str
    :param expect_raises: The expected exception to be raised.
    :type expect_raises: Exception

    :return: None
    """
    from PKPy.system_parser import Parser
    with pytest.raises(expect_raises):
        assert Parser(test).construct() == expected


expected_values = [[{'subcutaneous': 0, "time_span": 1000, 'dose': [20, 'continuous']}, [
    {'name': 'bloodstream', 'type': 'central', 'volume': 5000, 'initial_amount': 0.0,
     'rate_out': 1.0, 'rate_in': None},
    {'name': 'adipose', 'type': 'peripheral', 'volume': 1.0, 'initial_amount': 0.0,
     'rate_in': 1.0, 'rate_out': 1.0}]],
                   [{'subcutaneous': 0, "time_span": 1000, 'dose': [2, 'continuous']}, [
                       {'name': 'bloodstream', 'type': 'central', 'volume': 5000, 'initial_amount': 0.0,
                        'rate_out': 1.0, 'rate_in': None},
                       {'name': 'adipose', 'type': 'peripheral', 'volume': 1.0, 'initial_amount': 0.0, 'rate_in': 1.0,
                        'rate_out': 1.0},
                       {'name': 'adipose', 'type': 'peripheral', 'volume': 3000, 'initial_amount': 0.0, 'rate_in': 1.0,
                        'rate_out': 3}]]]


@pytest.mark.parametrize(
    "test, expected",
    [(f"PKPy/test/parser_tests_jsons/test_9.json", expected_values[0]),
     (f"PKPy/test/parser_tests_jsons/test_10.json", expected_values[1])])
def test_parser_for_wrong_output(test, expected):
    from PKPy.system_parser import Parser
    assert Parser(test).construct() == expected
