import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import utils


def test_get_book_details_repompts_for_invalid_input(monkeypatch):
    inputs = iter(["", "The Pragmatic Programmer", "Andrew Hunt", "not-a-year", "1999"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    title, author, year = utils.get_book_details()

    assert title == "The Pragmatic Programmer"
    assert author == "Andrew Hunt"
    assert year == 1999
