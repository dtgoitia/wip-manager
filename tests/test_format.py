from pathlib import Path

import pytest

from src.format import tidy_up_external_references


@pytest.mark.parametrize(
    ("untidy", "tidy"),
    (
        pytest.param(
            "\n".join(
                (
                    "- [ ] Task [1][1]",
                    "- [ ] Go [here](http://foo.bar/)",
                    "",
                    "<!-- External references -->",
                    "",
                    '[1]: https://example.com "Example page"',
                    "",
                )
            ),
            "\n".join(
                (
                    "- [ ] Task [1][1]",
                    "- [ ] Go [here][2]",
                    "",
                    "<!-- External references -->",
                    "",
                    '[1]: https://example.com "Example page"',
                    '[2]: http://foo.bar/ "?"',
                    "",
                )
            ),
            id="one_link_in_description",
        ),
        pytest.param(
            "\n".join(
                (
                    "- [ ] Task [1][1]",
                    "- [ ] Go [here](http://foo.bar/) and [there](https://example.com)",
                    "",
                    "<!-- External references -->",
                    "",
                    '[1]: https://example.com "Example page"',
                    "",
                )
            ),
            "\n".join(
                (
                    "- [ ] Task [1][1]",
                    "- [ ] Go [here][2] and [there][3]",
                    "",
                    "<!-- External references -->",
                    "",
                    '[1]: https://example.com "Example page"',
                    '[2]: http://foo.bar/ "?"',
                    '[3]: https://example.com "?"',
                    "",
                )
            ),
            id="many_links_in_description",
        ),
        pytest.param(
            "\n".join(
                (
                    "- [ ] Task [1][1]",
                    "- [ ] Go [here](http://foo.bar/) and [there](https://example.com)",
                    "  - Detail with [more notes](./baz.md)",
                    "",
                    "<!-- External references -->",
                    "",
                    '[1]: https://example.com "Example page"',
                    "",
                )
            ),
            "\n".join(
                (
                    "- [ ] Task [1][1]",
                    "- [ ] Go [here][2] and [there][3]",
                    "  - Detail with [more notes][4]",
                    "",
                    "<!-- External references -->",
                    "",
                    '[1]: https://example.com "Example page"',
                    '[2]: http://foo.bar/ "?"',
                    '[3]: https://example.com "?"',
                    '[4]: ./baz.md "?"',
                    "",
                )
            ),
            id="single_link_in_details",
        ),
        pytest.param(
            "\n".join(
                (
                    "- [ ] Task [1][1]",
                    "- [ ] Go [here](http://foo.bar/) and [there](https://example.com)",
                    "  - Detail with [more notes](./baz.md) and [more](./bazzz.md)",
                    "",
                    "<!-- External references -->",
                    "",
                    '[1]: https://example.com "Example page"',
                    "",
                )
            ),
            "\n".join(
                (
                    "- [ ] Task [1][1]",
                    "- [ ] Go [here][2] and [there][3]",
                    "  - Detail with [more notes][4] and [more][5]",
                    "",
                    "<!-- External references -->",
                    "",
                    '[1]: https://example.com "Example page"',
                    '[2]: http://foo.bar/ "?"',
                    '[3]: https://example.com "?"',
                    '[4]: ./baz.md "?"',
                    '[5]: ./bazzz.md "?"',
                    "",
                )
            ),
            id="many_links_in_details",
        ),
        # TODO
        # pytest.param(
        #     "\n".join(
        #         (
        #             "- [ ] Go [here](http://foo.bar/)",
        #             "",
        #         )
        #     ),
        #     "\n".join(
        #         (
        #             "- [ ] Go [here][1]",
        #             "",
        #             "<!-- External references -->",
        #             "",
        #             '[1]: http://foo.bar/ "?"',
        #             "",
        #         )
        #     ),
        #     id="add_external_references_header_if_missing",
        # ),
    ),
)
def test_tidy_up_external_references(tmp_path: Path, untidy: str, tidy: str) -> None:
    path = tmp_path / "wip.md"
    path.write_text(untidy)
    tidy_up_external_references(path=path)

    result = path.read_text()
    assert result == tidy
