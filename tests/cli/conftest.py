from pathlib import Path

import pytest


@pytest.fixture
def statics_dir() -> Path:
    return Path(__file__).parent / "statics"
