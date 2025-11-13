"""Example test file to demonstrate test structure."""

import pytest


def test_example():
    """Example test to verify pytest is working."""
    assert 1 + 1 == 2


@pytest.mark.unit
def test_unit_example():
    """Example unit test with marker."""
    assert True


@pytest.mark.slow
def test_slow_example():
    """Example slow test that can be skipped with pytest -m 'not slow'."""
    assert True
