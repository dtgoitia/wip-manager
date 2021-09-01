import pytest

from src.types import MarkdownStr, Task, parse


def test_parse_a_single_uncompleted_task():
    raw: MarkdownStr = "- [ ] Do foo"
    task = parse(raw)
    assert task == Task(description="Do foo", completed=False, details=[])


def test_parse_a_single_completed_task():
    raw: MarkdownStr = "- [x] Do foo"
    task = parse(raw)
    assert task == Task(description="Do foo", completed=True, details=[])


def test_parse_a_single_uncompleted_task_with_details():
    raw: MarkdownStr = (
        "- [ ] Do foo"
        "\n  - details line 1"
        "\n  - details line 2"
        "\n  - details line 3"
    )
    task = parse(raw)
    assert task == Task(
        description="Do foo",
        completed=False,
        details=[
            "details line 1",
            "details line 2",
            "details line 3",
        ],
    )


@pytest.mark.skip(reason="TODO")
def test_parse_a_single_uncompleted_task_with_tags():
    raw: MarkdownStr = "- [x] Do foo  #g:group1"
    assert raw


@pytest.mark.skip(reason="TODO")
def test_parse_multiple_tasks():
    ...


@pytest.mark.skip(reason="TODO")
def test_parse_and_restore_tasks_in_the_right_shape():
    ...
