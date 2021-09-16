import re
from typing import List

IS_HASH = re.compile(r"#([a-z0-9]{6})")  # `#34ja9i`


def assert_it_has_a_hash(with_hash: str, without_hash: str) -> None:
    if with_hash == without_hash:
        raise AssertionError(f"Strings must not be identical")

    different_chunks = diff_str(with_hash, without_hash)
    if len(different_chunks) != 1:
        raise AssertionError(f"Multiple different chunks found: {different_chunks}")

    chunk = different_chunks[0]
    clean_chunk = chunk.strip()  # the chunk may contain spaces around
    if not IS_HASH.match(clean_chunk):
        raise AssertionError(f"Different chunk must be a hash: {clean_chunk}")


def diff_str(string_a: str, string_b: str) -> str:
    """Find out what character sequences of the string A are missing in the string B.

    Assumption: A will always contain B, and some characters more - A's extra characters
    can be located anywhere and not necessarily continuously.
    """
    # diff: List[str] = []
    different_chunks: List[str] = []
    chunk: str = ""
    # last_matching_position = 0

    len_a = len(string_a)
    len_b = len(string_b)
    i_a = 0
    i_b = 0
    keep_reading_chars = True
    # print("")
    get_next_char_in_b = True
    while keep_reading_chars:
        # print(f"i_a={i_a}")
        # print(f"i_b={i_b}")
        if i_a < len_a:
            char_a = string_a[i_a]
        else:
            # we have reached the end of the string A
            char_a = None

        if i_b < len_b:
            char_b = string_b[i_b]
        else:
            # we have reached the end of the string B
            char_b = None
        # print(f"char_a={char_a}")
        # print(f"char_b={char_b}")
        # print(f"chunk={chunk}")

        if char_a == char_b:
            # last_matching_position = i_a
            if chunk:
                different_chunks.append(chunk)
                chunk = ""
            get_next_char_in_b = True
        else:
            chunk = f"{chunk}{char_a}"
            get_next_char_in_b = False

        if char_a is None and char_b is None:
            keep_reading_chars = False
        if char_a is not None:
            i_a += 1
        if get_next_char_in_b and char_b is not None:
            i_b += 1

    return different_chunks
