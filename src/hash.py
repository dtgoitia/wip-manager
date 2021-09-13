import hashlib
import uuid
from typing import NewType, Set

Hash = NewType("Hash", str)


def create_hash() -> Hash:
    # https://stackoverflow.com/q/4567089/8038693
    hash = hashlib.shake_128(str(uuid.uuid4()).encode("utf-8")).hexdigest(3)
    return Hash(hash)


def create_new_hash(existing: Set[Hash]) -> Hash:
    hash_already_exists = True
    while hash_already_exists:
        hash = create_hash()
        hash_already_exists = hash in existing
    return hash
