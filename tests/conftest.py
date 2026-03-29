"""Pytest configuration for django-iconx tests."""

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def _static_fixtures(settings):
    """Point STATICFILES_DIRS at test fixtures for all tests."""
    settings.STATICFILES_DIRS = [str(FIXTURES)]
