import pytest

from tests.string_comparison import assert_it_has_a_hash, diff_str


@pytest.mark.parametrize(
    ("string_a", "string_b", "expected_diff"),
    (
        pytest.param(
            "UNEXPECTED_abc",
            "_abc",
            ["UNEXPECTED"],
            id="one_unexpected_item_at_the_start",
        ),
        pytest.param(
            "abc_UNEXPECTED",
            "abc_",
            ["UNEXPECTED"],
            id="one_unexpected_item_at_the_end",
        ),
        pytest.param(
            "abc_UNEXPECTED_def",
            "abc__def",
            ["UNEXPECTED"],
            id="one_unexpected_item_in_the_middle",
        ),
        pytest.param(
            "aaa_FOO_bbb_BAR_ccc",
            "aaa__bbb__ccc",
            ["FOO", "BAR"],
            id="two_unexpected_items_in_the_middle",
        ),
    ),
)
def test_string_comparison(string_a, string_b, expected_diff):
    result = diff_str(string_a, string_b)
    assert result == expected_diff


def test_pass_assertion_if_it_has_no_hash():
    with_hash = "- [x] This is a completed task [here][1]  #g:group1 #8dc08c"
    without_hash = "- [x] This is a completed task [here][1]  #g:group1"

    assert_it_has_a_hash(with_hash=with_hash, without_hash=without_hash)


def test_fail_assertion_if_strings_are_identical():
    with_hash = "- [x] This is a completed task [here][1]  #g:group1"
    without_hash = "- [x] This is a completed task [here][1]  #g:group1"

    with pytest.raises(AssertionError) as e:
        assert_it_has_a_hash(with_hash=with_hash, without_hash=without_hash)

    exc = e.value

    assert exc.args == ("Strings must not be identical",)


def test_fail_assertion_if_different_chunk_is_not_a_hash():
    with_hash = "- [x] This is a completed task [here][1]  #g:group1 FOO"
    without_hash = "- [x] This is a completed task [here][1]  #g:group1"

    with pytest.raises(AssertionError) as e:
        assert_it_has_a_hash(with_hash=with_hash, without_hash=without_hash)

    exc = e.value

    assert exc.args == ("Different chunk must be a hash: FOO",)


def test_fail_assertion_if_many_different_chunks_found():
    string_a = "- [x] This is a BIG task [here][1]  #g:group1 FOO"
    string_b = "- [x] This is a task [here][1]  #g:group1"

    with pytest.raises(AssertionError) as e:
        assert_it_has_a_hash(with_hash=string_a, without_hash=string_b)

    exc = e.value

    assert exc.args == ("Multiple different chunks found: ['BIG ', ' FOO']",)
