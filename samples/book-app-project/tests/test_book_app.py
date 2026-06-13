import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import book_app
import books
from books import BookCollection


def _make_input(values):
    iterator = iter(values)
    return lambda prompt="": next(iterator)


def test_handle_find_year_range(monkeypatch, capsys, tmp_path):
    temp_file = tmp_path / "data.json"
    temp_file.write_text("[]")
    monkeypatch.setattr(books, "DATA_FILE", str(temp_file))
    monkeypatch.setattr(book_app, "collection", BookCollection())

    book_app.collection.add_book("Book One", "Author A", 1998)
    book_app.collection.add_book("Book Two", "Author B", 2005)
    book_app.collection.add_book("Book Three", "Author C", 2010)

    monkeypatch.setattr("builtins.input", _make_input(["2000", "2010"]))

    book_app.handle_find_year_range()

    output = capsys.readouterr().out
    assert "Find Books by Year Range" in output
    assert "Book Two" in output
    assert "Book Three" in output
    assert "Book One" not in output


def test_handle_find_year_range_shows_validation_error(monkeypatch, capsys, tmp_path):
    temp_file = tmp_path / "data.json"
    temp_file.write_text("[]")
    monkeypatch.setattr(books, "DATA_FILE", str(temp_file))
    monkeypatch.setattr(book_app, "collection", BookCollection())

    monkeypatch.setattr("builtins.input", _make_input(["2020", "2010"]))

    book_app.handle_find_year_range()

    output = capsys.readouterr().out
    assert "Start year cannot be greater than end year." in output
