import pytest

from src.hash import Hash, create_hash, create_new_hash


@pytest.mark.skip(reason="only for developent purposes")
def test_create_hash():
    hash = create_hash()
    assert hash


def test_create_new_hash():
    existing_hashes = {Hash("000000"), Hash("000001")}
    new_hash = create_new_hash(existing=existing_hashes)
    assert new_hash not in existing_hashes
