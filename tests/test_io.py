from src.io import json_dumps_with_trailing_comma, json_loads_with_trailing_comma


def test_read_with_trailing_comma():
    json_str = "\n".join(
        (
            "{",
            '  "a": 1,',
            '  "b": [',
            "    1,",
            "    2,",
            "    3,",
            "    4,",
            '    "looooooooooooooooooooooooooooooooooooooong line",',
            "  ],",
            '  "c": {',
            '    "c1": 1,',
            '    "c2": "looooooooooooooooooooooooooooooooooooooong line",',
            "  },",
            "}",
        )
    )

    data = json_loads_with_trailing_comma(json_str)

    assert data == {
        "a": 1,
        "b": [
            1,
            2,
            3,
            4,
            "looooooooooooooooooooooooooooooooooooooong line",
        ],
        "c": {
            "c1": 1,
            "c2": "looooooooooooooooooooooooooooooooooooooong line",
        },
    }


def test_add_trailing_comma():
    data = {
        "a": 1,
        "b": [
            1,
            2,
            3,
            4,
            "looooooooooooooooooooooooooooooooooooooong line",
        ],
        "c": {
            "c1": 1,
            "c2": "looooooooooooooooooooooooooooooooooooooong line",
        },
    }

    json_str = json_dumps_with_trailing_comma(data)

    assert json_str == "\n".join(
        (
            "{",
            '  "a": 1,',
            '  "b": [',
            "    1,",
            "    2,",
            "    3,",
            "    4,",
            '    "looooooooooooooooooooooooooooooooooooooong line",',
            "  ],",
            '  "c": {',
            '    "c1": 1,',
            '    "c2": "looooooooooooooooooooooooooooooooooooooong line",',
            "  },",
            "}",
        )
    )
