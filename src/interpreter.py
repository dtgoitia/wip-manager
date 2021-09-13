from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Iterator, List, Optional, Set, Union, cast

from src.hash import Hash
from src.types import (
    EmptyLine,
    ExternalReference,
    ExternalReferencesHeader,
    Item,
    MarkdownStr,
    Tag,
    Task,
    TaskDetail,
    Title,
)

NEW_LINE = "\n"


@dataclass
class TokenizedLine:
    line_number: int
    tokens: List[Token]

    @property
    def types(self) -> Set:
        token_classes = (token.__class__ for token in self.tokens)
        return set(token_classes)


@dataclass
class IncompleteSymbol:
    # `- [ ] `
    ...


@dataclass
class CompletedSymbol:
    # `- [x] `
    ...


@dataclass
class TagToken:
    # Don't make "type" an enum, because it will cause you problems to add new tags via
    # config, or parse unknown tags
    token: str


@dataclass
class HashToken:
    hash: str


@dataclass
class Text:
    text: str


@dataclass
class Indentation:
    spaces: int


@dataclass
class BulletPointPrefix:
    ...


@dataclass
class EmptyLineToken:
    ...


@dataclass
class TitleToken:
    title: str


@dataclass
class ExternalReferenceToken:
    number: int
    path: str
    description: str


@dataclass
class ExternalReferencesHeaderToken:
    ...


Token = Union[
    IncompleteSymbol,
    CompletedSymbol,
    TagToken,
    Text,
    Indentation,
    BulletPointPrefix,
    EmptyLineToken,
    TitleToken,
    ExternalReferenceToken,
    ExternalReferencesHeaderToken,
    HashToken,
]


def tokenize_document(document: str) -> Iterator[TokenizedLine]:
    for line_number, line in enumerate(document.split(NEW_LINE)):
        yield TokenizedLine(line_number=line_number + 1, tokens=tokenize_line(line))


HAS_DONE_PREFIX = re.compile(r"^- \[x\]\s")  # starts with `- [x] `
HAS_INCOMPLETE_PREFIX = re.compile(r"^(- \[\s\]\s)")  # starts with `- [ ] `
INDENTATION_PATTERN = re.compile(r"^(\s*)")  # spaces
HAS_BULLET_POINT_PREFIX = re.compile(r"^-\s")
HAS_TAGS = re.compile(r"\s#([a-z]:[a-z0-9-_,]*)")  # `#g:group1_b`
HAS_HASH = re.compile(r"\s#([a-z0-9]{6})$")  # `#34ja9i`
EXTERNAL_REFERENCE_PATTERN = re.compile(r'^\[([0-9]+)\]: ([^\s]+)\s"(.*)"$')


def tokenize_line(original_line: str) -> List[Token]:
    tokens: List[Token] = []

    # line from which identified tokens will substracted token by token
    line = original_line

    if not line:
        return [EmptyLineToken()]

    # Tokenize H2 title
    if line.startswith("##"):
        title = line.replace("## ", "", 1)
        token = TitleToken(title=title)
        return [token]

    # Tokenize external reference
    if matches := EXTERNAL_REFERENCE_PATTERN.match(line):
        return [
            ExternalReferenceToken(
                number=int(matches.group(1)),
                path=matches.group(2),
                description=matches.group(3),
            )
        ]

    # Tokenize external references header
    if line == "<!-- External references -->":
        return [ExternalReferencesHeaderToken()]

    # Tokenize indentation
    if line.startswith(" "):
        indentation = INDENTATION_PATTERN.match(line).group(1)  # type:ignore
        space_amount = len(indentation)
        tokens.append(Indentation(spaces=space_amount))
        line = line.replace(indentation, "", 1)

    # Tokenize done/todo prefix
    if HAS_DONE_PREFIX.match(line):
        tokens.append(CompletedSymbol())
        line = line.replace("- [x] ", "", 1)
    elif HAS_INCOMPLETE_PREFIX.match(line):
        tokens.append(IncompleteSymbol())
        line = line.replace("- [ ] ", "", 1)
    elif HAS_BULLET_POINT_PREFIX.match(line):
        tokens.append(BulletPointPrefix())
        line = line.replace("- ", "", 1)

    # Tokenize hash
    hash_token: Optional[HashToken] = None
    if matches := HAS_HASH.search(line):
        hash_str = matches.group(1)
        hash_token = HashToken(hash=hash_str)
        line = line.replace(f" #{hash_str}", "", 1)

    # Tokenize tag
    tag_tokens: List[TagToken] = []
    if raw_tags := HAS_TAGS.findall(line):
        for raw_tag in raw_tags:
            tag_tokens.append(TagToken(token=raw_tag))
            line = line.replace(f" #{raw_tag}", "", 1)

    if tag_tokens or hash_token:
        # remove double space between the text and the tags/hash
        line = line.rstrip(" ")

    # Tokenize text
    if line:
        tokens.append(Text(text=line))

    # Add tags after text
    if tag_tokens:
        tokens.extend(tag_tokens)

    # Add hash at the end
    if hash_token:
        tokens.append(hash_token)

    return tokens


PseudoItem = Union[Item, TaskDetail]

# NOTE: failing if you find a tag outside a task is something that should happen in
# the lexical analysis, not in the tokenization. Tokenization failures should be if
# there is an incorrect syntax, etc.


def analyse_lexically(document: Iterator[TokenizedLine]) -> List[Item]:
    """
    Line by line:
        1. interpret line using its tokens
        2. check if buffer exists
        3. decide if to flush buffer or to compose with buffer
    """
    parsed_items: List[Item] = []
    buffer: Optional[PseudoItem] = None
    for line in document:
        token_types = line.types

        if is_empty_line(token_types):
            if buffer:
                parsed_items.append(cast(Item, buffer))
                buffer = None

            empty_line = EmptyLine()
            parsed_items.append(empty_line)
            continue

        if is_task(token_types):
            task = parse_task(line)
            if buffer:
                parsed_items.append(cast(Item, buffer))
            buffer = task

        if is_detail(token_types):
            detail = parse_task_detail(line)
            if not buffer:
                raise ValueError("You cannot have details outside a task")
            else:
                # Compose detail with task in buffer
                partially_parsed_task = cast(Task, buffer)
                updated_task = partially_parsed_task.add_detail(detail)
                buffer = updated_task
                continue

        if is_external_references_header(token_types):
            previous_line = parsed_items[-1]
            if not isinstance(previous_line, EmptyLine):
                raise ValueError("Empty line expected before external reference header")

            external_references_header = ExternalReferencesHeader()
            next_line = next(document)
            if not is_empty_line(next_line.types):
                raise ValueError("Empty line expected after external reference header")

            parsed_items.append(external_references_header)
            parsed_items.append(EmptyLine())

            buffer = None
            continue

        if is_external_reference(token_types):
            if buffer:
                raise ValueError("Empty line expected before external references")

            external_reference = parse_external_reference(line)
            parsed_items.append(external_reference)
            # TODO: ensure that once you find the first external reference, nothing
            # else can be added to the WIP file
            continue

        if is_title(token_types):
            assert not buffer, "I didn't expect to have anyhting bufered at this point"

            title = parse_title(line)
            parsed_items.append(title)

            continue

    if buffer:
        parsed_items.append(cast(Item, buffer))

    return parsed_items


def is_empty_line(token_types: Set) -> bool:
    return {EmptyLineToken} == token_types


def is_task(token_types: Set) -> bool:
    """Drop expected token types, if any left, return False"""
    remaining_tokens = token_types

    # Must have text
    if Text in token_types:
        remaining_tokens = remaining_tokens - {Text}
    else:
        return False

    # Must have completed/incomplete prefix
    if IncompleteSymbol in token_types or CompletedSymbol in token_types:
        remaining_tokens = remaining_tokens - {IncompleteSymbol, CompletedSymbol}
    else:
        return False

    # Can have tags
    if TagToken in token_types:
        remaining_tokens = remaining_tokens - {TagToken}

    # Can have hash
    if HashToken in token_types:
        remaining_tokens = remaining_tokens - {HashToken}

    if remaining_tokens:
        return False

    return True


def is_detail(token_types: Set) -> bool:
    return {Indentation, BulletPointPrefix, Text} == token_types


def is_external_references_header(token_types: Set) -> bool:
    return {ExternalReferencesHeaderToken} == token_types


def is_external_reference(token_types: Set) -> bool:
    return {ExternalReferenceToken} == token_types


def is_title(token_types: Set) -> bool:
    return {TitleToken} == token_types


def parse_tag_token(tag: TagToken) -> Tag:
    _type, value = tag.token.split(":")
    return Tag(type=_type, value=value)


def parse_task(line: TokenizedLine) -> Task:
    prefix = line.tokens[0]

    tag_tokens = [token for token in line.tokens if isinstance(token, TagToken)]

    hash_tokens = [token for token in line.tokens if isinstance(token, HashToken)]

    return Task(
        done=prefix == CompletedSymbol(),
        description=cast(Text, line.tokens[1]).text,
        tags=[parse_tag_token(token) for token in tag_tokens],
        details=[],
        hash=Hash(hash_tokens[0].hash) if hash_tokens else None,
    )


def parse_task_detail(line: TokenizedLine) -> TaskDetail:
    indentation = next(token for token in line.tokens if isinstance(token, Indentation))
    assert indentation.spaces == 2, "Only a 2 space indentation is supported"

    text = next(token for token in line.tokens if isinstance(token, Text))
    task_detail = TaskDetail(description=text.text)
    return task_detail


def parse_external_reference(line: TokenizedLine) -> ExternalReference:
    for token in line.tokens:
        if isinstance(token, ExternalReferenceToken):
            return ExternalReference(
                number=token.number,
                path=token.path,
                description=token.description,
            )
    raise NotImplementedError("Oops, I didn't expect to reach here")


def parse_title(line: TokenizedLine) -> Title:
    title = cast(TitleToken, line.tokens[0])
    return Title(title=title.title)


def parse_document(raw: MarkdownStr) -> List[Item]:
    tokenized_lines = tokenize_document(raw)
    items = analyse_lexically(tokenized_lines)
    return items


def items_to_markdown(data: Iterable[Item]) -> MarkdownStr:
    lines = [item.to_str() for item in data]
    content = "\n".join(lines)
    return content
