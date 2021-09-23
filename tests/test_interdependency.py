from src.interdependency import assert_completed_tasks_have_no_pending_prior_task
from src.interpreter import parse_document
from src.types import MarkdownStr


def test_assert_all_completed_tasks_have_all_previous_tasks_completed():
    raw: MarkdownStr = "\n".join(
        (
            "- [ ] First task  #xxxxx1",
            "- [x] Second task  #r:after-xxxxx1 #xxxxx2",
        )
    )
    items = parse_document(raw)
    assert_completed_tasks_have_no_pending_prior_task(items)
