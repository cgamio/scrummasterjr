import pytest
from unittest.mock import MagicMock
import logging

@pytest.fixture(autouse=True)
def mock_bolt_client():
    logging.debug("mock_bolt_client was called")
    mock_client = MagicMock()

    from scrummasterjr import app
    app.client = mock_client
    logging.debug(f"app.client = {app.client}")
