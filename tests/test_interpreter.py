import pytest

from src.interpreter import (
    BulletPointPrefix,
    CompletedSymbol,
    EmptyLineToken,
    ExternalReferencesHeaderToken,
    ExternalReferenceToken,
    IncompleteSymbol,
    Indentation,
    Tag,
    TagToken,
    Task,
    Text,
    TitleToken,
    TokenizedLine,
    is_detail,
    is_empty_line,
    is_external_reference,
    is_external_references_header,
    is_task,
    is_title,
    items_to_markdown,
    parse_document,
    parse_external_reference,
    parse_tag_token,
    parse_task_detail,
    parse_title,
    tokenize_document,
    tokenize_line,
)
from src.types import ExternalReference, MarkdownStr, TaskDetail, Title


@pytest.mark.parametrize(
    ("line", "expected"),
    (
        pytest.param(
            "- [ ] Foo",
            [IncompleteSymbol(), Text(text="Foo")],
            id="incompleted_task",
        ),
        pytest.param(
            "- [x] Foo",
            [CompletedSymbol(), Text(text="Foo")],
            id="completed_task",
        ),
        pytest.param(
            "- [ ] Foo bar - baz",
            [IncompleteSymbol(), Text(text="Foo bar - baz")],
            id="task_with_hyphen",
        ),
        pytest.param(
            "- [ ] Foo  #g:group1",
            [
                IncompleteSymbol(),
                Text(text="Foo"),
                TagToken(token="g:group1"),
            ],
            id="incompleted_task_with_one_tag",
        ),
        pytest.param(
            "- [ ] Foo  #g:g1 #g:g2 #p:urgent",
            [
                IncompleteSymbol(),
                Text(text="Foo"),
                TagToken(token="g:g1"),
                TagToken(token="g:g2"),
                TagToken(token="p:urgent"),
            ],
            id="incompleted_task_with_many_tags",
        ),
        pytest.param(
            "  - Detail of task",
            [
                Indentation(spaces=2),
                BulletPointPrefix(),
                Text(text="Detail of task"),
            ],
            id="task_detail",
        ),
        pytest.param(
            "  - Detail of task - foo",
            [
                Indentation(spaces=2),
                BulletPointPrefix(),
                Text(text="Detail of task - foo"),
            ],
            id="task_detail_with_hyphen",
        ),
        pytest.param("", [EmptyLineToken()], id="empty_line"),
        pytest.param("## Bar", [TitleToken(title="Bar")], id="title"),
        pytest.param(
            '[23]: https://example.com/a-1_U "website"',
            [
                ExternalReferenceToken(
                    number=23,
                    path="https://example.com/a-1_U",
                    description="website",
                )
            ],
            id="external_reference",
        ),
        pytest.param(
            "<!-- External references -->",
            [ExternalReferencesHeaderToken()],
            id="external_references_header",
        ),
    ),
)
def test_tokenize_line(line, expected):
    result = tokenize_line(line)
    assert result == expected


def test_tokenize_document():
    raw_document: MarkdownStr = "\n".join(
        (
            "## Tasks to focus on",
            "",
            "- [ ] Task for today #g:g1 #g:g2 #p:urgent",
            "",
            "## Backlog",
            "",
            "- [ ] Task",
            "",
            "<!-- External references -->",
            "",
            '[1]: https://example.com "Example page"',
            "",
        )
    )
    tokens = list(tokenize_document(raw_document))
    assert tokens == [
        TokenizedLine(line_number=1, tokens=[TitleToken(title="Tasks to focus on")]),
        TokenizedLine(line_number=2, tokens=[EmptyLineToken()]),
        TokenizedLine(
            line_number=3,
            tokens=[
                IncompleteSymbol(),
                Text(text="Task for today"),
                TagToken(token="g:g1"),
                TagToken(token="g:g2"),
                TagToken(token="p:urgent"),
            ],
        ),
        TokenizedLine(line_number=4, tokens=[EmptyLineToken()]),
        TokenizedLine(line_number=5, tokens=[TitleToken(title="Backlog")]),
        TokenizedLine(line_number=6, tokens=[EmptyLineToken()]),
        TokenizedLine(line_number=7, tokens=[IncompleteSymbol(), Text(text="Task")]),
        TokenizedLine(line_number=8, tokens=[EmptyLineToken()]),
        TokenizedLine(line_number=9, tokens=[ExternalReferencesHeaderToken()]),
        TokenizedLine(line_number=10, tokens=[EmptyLineToken()]),
        TokenizedLine(
            line_number=11,
            tokens=[
                ExternalReferenceToken(
                    number=1,
                    path="https://example.com",
                    description="Example page",
                )
            ],
        ),
        TokenizedLine(line_number=12, tokens=[EmptyLineToken()]),
    ]


@pytest.mark.parametrize(
    ("token_types", "expected"),
    (
        pytest.param({EmptyLineToken}, True, id="empty_line"),
        pytest.param({EmptyLineToken, Text}, False, id="non_empty_line"),
    ),
)
def test_is_empty_line(token_types, expected):
    assert is_empty_line(token_types) is expected


@pytest.mark.parametrize(
    ("token_types", "expected"),
    (
        pytest.param({IncompleteSymbol, Text}, True, id="incomplete_task"),
        pytest.param({CompletedSymbol, Text}, True, id="completed_task"),
        pytest.param({IncompleteSymbol, Text, TagToken}, True, id="task_with_tags"),
        pytest.param({Indentation, IncompleteSymbol, Text}, False, id="wrong_task"),
    ),
)
def test_is_task(token_types, expected):
    assert is_task(token_types) is expected


@pytest.mark.parametrize(
    ("token_types", "expected"),
    (
        pytest.param({Indentation, BulletPointPrefix, Text}, True, id="detail"),
        pytest.param({BulletPointPrefix, Text}, False, id="must_have_indentation"),
        pytest.param({Indentation, Text}, False, id="must_have_bullet_point"),
        pytest.param({Indentation, BulletPointPrefix}, False, id="must_have_text"),
    ),
)
def test_is_detail(token_types, expected):
    assert is_detail(token_types) is expected


@pytest.mark.parametrize(
    ("token_types", "expected"),
    (
        pytest.param(
            {ExternalReferencesHeaderToken}, True, id="external_references_header"
        ),
        pytest.param({ExternalReferencesHeaderToken, Text}, False, id="wrong_header"),
    ),
)
def test_is_external_references_header(token_types, expected):
    assert is_external_references_header(token_types) is expected


@pytest.mark.parametrize(
    ("token_types", "expected"),
    (
        pytest.param({ExternalReferenceToken}, True, id="external_reference"),
        pytest.param(
            {ExternalReferenceToken, Text}, False, id="wrong_external_reference"
        ),
    ),
)
def test_is_external_references(token_types, expected):
    assert is_external_reference(token_types) is expected


@pytest.mark.parametrize(
    ("token_types", "expected"),
    (
        pytest.param({TitleToken}, True, id="title"),
        pytest.param({TitleToken, Text}, False, id="wrong_title"),
    ),
)
def test_is_title(token_types, expected):
    assert is_title(token_types) is expected


def test_parse_tag_token():
    token = TagToken("g:foo")
    tag = parse_tag_token(token)
    assert tag == Tag(type="g", value="foo")


def test_parse_task_detail():
    line = TokenizedLine(
        line_number=0,
        tokens=[Indentation(spaces=2), BulletPointPrefix(), Text(text="I'm a detail")],
    )
    task_detail = parse_task_detail(line)
    assert task_detail == TaskDetail(description="I'm a detail")


def test_parse_external_reference():
    line = TokenizedLine(
        line_number=0,
        tokens=[
            ExternalReferenceToken(number=2, path="https://foo.eu", description="foo")
        ],
    )
    text = parse_external_reference(line)
    assert text == ExternalReference(number=2, path="https://foo.eu", description="foo")


def test_parse_title():
    line = TokenizedLine(
        line_number=0,
        tokens=[TitleToken(title="any text")],
    )
    text = parse_title(line)
    assert text == Title(title="any text")


def test_add_detail_to_task():
    task = Task(done=True, description="Do", tags=[], details=[])
    detail = TaskDetail(description="Detail")
    updated_task = task.add_detail(detail)
    assert updated_task == Task(
        done=True,
        description="Do",
        tags=[],
        details=[TaskDetail(description="Detail")],
    )


def test_parse_a_single_uncompleted_task_with_details():
    raw: MarkdownStr = (
        "- [ ] Do foo"
        "\n  - details line 1"
        "\n  - details line 2"
        "\n  - details line 3"
    )
    items = parse_document(raw)
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


def test_parse_multiple_tasks():
    raw: MarkdownStr = (
        "- [ ] Do foo  #g:group1\n"
        "- [ ] Do bar\n"
        "  - Some details\n"
        "- [ ] Do baz  #p:priority_a"
    )
    tasks = parse_document(raw)
    assert tasks == [
        Task(
            description="Do foo",
            done=False,
            details=[],
            tags=[Tag(type="g", value="group1")],
        ),
        Task(
            description="Do bar",
            done=False,
            details=[TaskDetail(description="Some details")],
            tags=[],
        ),
        Task(
            description="Do baz",
            done=False,
            details=[],
            tags=[Tag(type="p", value="priority_a")],
        ),
    ]


def test_parse_and_restore_tasks_in_the_right_shape():
    raw: MarkdownStr = (
        "- [ ] Do foo  #g:group1\n"
        "- [ ] Do bar\n"
        "  - Some details\n"
        "- [ ] Do baz  #p:priority_a"
    )
    tasks = parse_document(raw)
    parsed_raw = items_to_markdown(tasks)
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
    items = parse_document(raw)
    parsed_raw = items_to_markdown(items)
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
    items = parse_document(raw)
    parsed_raw = items_to_markdown(items)
    assert raw == parsed_raw


# TODO: move to test_parser once the deserialize_content function is in parser.py
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
    items = parse_document(raw)
    parsed_raw = items_to_markdown(items)
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
