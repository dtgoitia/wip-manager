import pytest

from src.types import (
    MarkdownStr,
    Task,
    TaskDetail,
    Title,
    deserialize_content,
    is_external_reference,
    is_external_references_header,
    is_title,
    parse_items,
    parse_task,
    parse_task_detail,
    parse_title,
)


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
    items = parse_items(raw)
    assert items == [
        Task(
            description="Do foo",
            done=False,
            details=[
                TaskDetail(description="details line 1"),
                TaskDetail(description="details line 2"),
                TaskDetail(description="details line 3"),
            ],
            tags=[],
        )
    ]


def test_parse_a_task_with_hyphen():
    raw: MarkdownStr = "- [ ] Do foo - bar"
    tasks = parse_items(raw)
    content = tasks
    parsed_raw = deserialize_content(content)
    assert raw == parsed_raw


def test_parse_a_detail():
    raw: MarkdownStr = "  - line with details"
    detail = parse_task_detail(raw)
    assert detail == TaskDetail(description="line with details")


def test_parse_a_detail_with_hyphen():
    raw: MarkdownStr = "  - line with details - and a hyphen"
    detail = parse_task_detail(raw)
    assert detail == TaskDetail(description="line with details - and a hyphen")


def test_parse_a_task_with_tags():
    raw: MarkdownStr = "- [ ] Do foo  #g:group1 #p:urgent"
    task = parse_task(raw)
    assert task.tags == ["g:group1", "p:urgent"]


def test_parse_multiple_tasks():
    raw: MarkdownStr = (
        "- [ ] Do foo  #g:group1\n"
        "- [ ] Do bar\n"
        "  - Some details\n"
        "- [ ] Do baz  #p:priority_a"
    )
    tasks = parse_items(raw)
    assert tasks == [
        Task(description="Do foo", done=False, details=[], tags=["g:group1"]),
        Task(
            description="Do bar",
            done=False,
            details=[TaskDetail(description="Some details")],
            tags=[],
        ),
        Task(description="Do baz", done=False, details=[], tags=["p:priority_a"]),
    ]


def test_parse_and_restore_tasks_in_the_right_shape():
    raw: MarkdownStr = (
        "- [ ] Do foo  #g:group1\n"
        "- [ ] Do bar\n"
        "  - Some details\n"
        "- [ ] Do baz  #p:priority_a"
    )
    tasks = parse_items(raw)
    parsed_raw = deserialize_content(tasks)
    assert raw == parsed_raw


def test_parse_external_references_header():
    raw: MarkdownStr = "\n".join(
        [
            "- [ ] Last task",
            "",
            "<!-- External references -->",
            "",
        ]
    )
    items = parse_items(raw)
    parsed_raw = deserialize_content(items)
    assert raw == parsed_raw


def test_parse_external_references():
    raw: MarkdownStr = "\n".join(
        (
            "- [ ] Last task",
            "",
            "<!-- External references -->",
            "",
            '[1]: https://example.com "Example page"',
            '[2]: https://example2.com "Example page 2"',
            "",
        )
    )
    items = parse_items(raw)
    parsed_raw = deserialize_content(items)
    assert raw == parsed_raw


def test_line_is_external_references_header():
    line = "<!-- External references -->"
    result = is_external_references_header(line)
    assert result is True


def test_line_is_external_reference():
    line = '[1]: https://example.com/a-1_U "Example page"'
    result = is_external_reference(line)
    assert result is True


@pytest.mark.parametrize(
    ("raw_line"),
    (
        pytest.param("## Tasks to focus on", id="focus_tasks_title"),
        pytest.param("## Backlog", id="backlog_title"),
    ),
)
def test_line_is_title(raw_line):
    result = is_title(raw_line)
    assert result is True


def test_parse_title():
    raw: MarkdownStr = "## Tasks to focus on"
    title = parse_title(raw)
    assert title == Title(title="Tasks to focus on")


def test_parse_wip_document_with_titles():
    raw: MarkdownStr = "\n".join(
        (
            "## Tasks to focus on",
            "",
            "- [ ] Task for today",
            "",
            "## Backlog",
            "",
            "- [ ] Future task",
            "",
            "<!-- External references -->",
            "",
            '[1]: https://example.com "Example page"',
            "",
        )
    )
    items = parse_items(raw)
    parsed_raw = deserialize_content(items)
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
