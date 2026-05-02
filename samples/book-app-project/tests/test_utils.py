import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import patch
from io import StringIO
from utils import get_user_choice


def test_get_user_choice_valid_input():
    """Test that valid input (1-5) returns immediately."""
    with patch('builtins.input', return_value='3'):
        result = get_user_choice()
        assert result == '3'


def test_get_user_choice_all_valid_options():
    """Test all valid choices (1-5)."""
    for option in ['1', '2', '3', '4', '5']:
        with patch('builtins.input', return_value=option):
            result = get_user_choice()
            assert result == option


def test_get_user_choice_empty_input_then_valid():
    """Test that empty input is rejected and re-prompted."""
    with patch('builtins.input', side_effect=['', '2']), \
         patch('sys.stdout', new=StringIO()) as fake_out:
        result = get_user_choice()
        assert result == '2'
        output = fake_out.getvalue()
        assert 'Please enter a choice.' in output


def test_get_user_choice_non_numeric_then_valid():
    """Test that non-numeric input is rejected and re-prompted."""
    with patch('builtins.input', side_effect=['abc', '4']), \
         patch('sys.stdout', new=StringIO()) as fake_out:
        result = get_user_choice()
        assert result == '4'
        output = fake_out.getvalue()
        assert 'Please enter a number.' in output


def test_get_user_choice_out_of_range_then_valid():
    """Test that out-of-range input is rejected and re-prompted."""
    with patch('builtins.input', side_effect=['9', '1']), \
         patch('sys.stdout', new=StringIO()) as fake_out:
        result = get_user_choice()
        assert result == '1'
        output = fake_out.getvalue()
        assert 'Please enter a number between 1 and 5.' in output


def test_get_user_choice_zero_then_valid():
    """Test that zero is rejected as out-of-range."""
    with patch('builtins.input', side_effect=['0', '5']), \
         patch('sys.stdout', new=StringIO()) as fake_out:
        result = get_user_choice()
        assert result == '5'
        output = fake_out.getvalue()
        assert 'Please enter a number between 1 and 5.' in output


def test_get_user_choice_multiple_invalid_inputs():
    """Test multiple invalid inputs before valid one."""
    with patch('builtins.input', side_effect=['', 'x', '10', '3']), \
         patch('sys.stdout', new=StringIO()) as fake_out:
        result = get_user_choice()
        assert result == '3'
        output = fake_out.getvalue()
        # Should see all error messages
        assert 'Please enter a choice.' in output
        assert 'Please enter a number.' in output
        assert 'Please enter a number between 1 and 5.' in output


def test_get_user_choice_whitespace_handling():
    """Test that leading/trailing whitespace is stripped."""
    with patch('builtins.input', return_value='  2  '):
        result = get_user_choice()
        assert result == '2'
