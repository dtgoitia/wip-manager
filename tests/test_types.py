import pytest

from src.types import MarkdownStr, Task, deserialize_content, parse, parse_task


def test_parse_a_single_uncompleted_task():
    raw: MarkdownStr = "- [ ] Do foo"
    task = parse_task(raw)
    assert task == Task(description="Do foo", done=False, details=[], tags=[])


def test_parse_a_single_completed_task():
    raw: MarkdownStr = "- [x] Do foo"
    task = parse_task(raw)
    assert task == Task(description="Do foo", done=True, details=[], tags=[])


def test_parse_a_single_uncompleted_task_with_details():
    raw: MarkdownStr = (
        "- [ ] Do foo"
        "\n  - details line 1"
        "\n  - details line 2"
        "\n  - details line 3"
    )
    task = parse_task(raw)
    assert task == Task(
        description="Do foo",
        done=False,
        details=[
            "details line 1",
            "details line 2",
            "details line 3",
        ],
        tags=[],
    )


def test_parse_a_single_uncompleted_task_with_tags():
    raw: MarkdownStr = "- [ ] Do foo  #g:group1"
    task = parse_task(raw)
    assert task == Task(
        description="Do foo",  # do not show tags in the description
        done=False,
        details=[],
        tags=["g:group1"],
    )


def test_parse_multiple_tasks():
    raw: MarkdownStr = (
        "- [ ] Do foo  #g:group1\n"
        "- [ ] Do bar\n"
        "  - Some details\n"
        "- [ ] Do baz  #p:priority_a"
    )
    tasks = parse(raw)
    assert tasks == [
        Task(description="Do foo", done=False, details=[], tags=["g:group1"]),
        Task(description="Do bar", done=False, details=["Some details"], tags=[]),
        Task(description="Do baz", done=False, details=[], tags=["p:priority_a"]),
    ]


def test_parse_and_restore_tasks_in_the_right_shape():
    raw: MarkdownStr = (
        "- [ ] Do foo  #g:group1\n"
        "- [ ] Do bar\n"
        "  - Some details\n"
        "- [ ] Do baz  #p:priority_a"
    )
    tasks = parse(raw)
    parsed_raw = deserialize_content(tasks)
    assert raw == parsed_raw


@pytest.mark.skip(reason="TODO")
def test_parse_empty_lines_between_tasks():
    ...


@pytest.mark.skip(reason="TODO")
def test_parse_board_and_backlog_format():
    ...


@pytest.mark.skip(reason="TODO")
def test_seralize_to_board_and_backlog_format():
    ...


@pytest.mark.skip(reason="TODO")
def test_ignore_markdown_comments_in_task_details():
    """This is not a hard constrain, but simplifies parsing logic.
    Unless this feature is required do not complicate yourself.
    """
    ...


@pytest.mark.skip(reason="TODO")
def test_fail_validation_if_a_task_has_repeated_tags():
    ...
