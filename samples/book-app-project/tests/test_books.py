import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import books
from books import BookCollection


@pytest.fixture(autouse=True)
def use_temp_data_file(tmp_path, monkeypatch):
    """Use a temporary data file for each test."""
    temp_file = tmp_path / "data.json"
    temp_file.write_text("[]")
    monkeypatch.setattr(books, "DATA_FILE", str(temp_file))


def test_add_book():
    collection = BookCollection()
    initial_count = len(collection.books)
    collection.add_book("1984", "George Orwell", 1949)
    assert len(collection.books) == initial_count + 1
    book = collection.find_book_by_title("1984")
    assert book is not None
    assert book.author == "George Orwell"
    assert book.year == 1949
    assert book.read is False

def test_mark_book_as_read():
    collection = BookCollection()
    collection.add_book("Dune", "Frank Herbert", 1965)
    result = collection.mark_as_read("Dune")
    assert result is True
    book = collection.find_book_by_title("Dune")
    assert book.read is True

def test_mark_book_as_read_invalid():
    collection = BookCollection()
    result = collection.mark_as_read("Nonexistent Book")
    assert result is False

def test_remove_book():
    collection = BookCollection()
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
    result = collection.remove_book("The Hobbit")
    assert result is True
    book = collection.find_book_by_title("The Hobbit")
    assert book is None

def test_remove_book_invalid():
    collection = BookCollection()
    result = collection.remove_book("Nonexistent Book")
    assert result is False


def test_load_books_skips_invalid_records(tmp_path, monkeypatch):
    temp_file = tmp_path / "data.json"
    temp_file.write_text(
        """
[
  {"title": "Valid", "author": "Author", "year": 2000, "read": false},
  {"author": "Missing title", "year": 2001},
  "not a book"
]
""".strip()
    )
    monkeypatch.setattr(books, "DATA_FILE", temp_file)

    collection = BookCollection()

    assert len(collection.books) == 1
    assert collection.books[0].title == "Valid"


def test_add_book_rejects_invalid_year():
    collection = BookCollection()

    with pytest.raises(ValueError, match="Book year must be an integer"):
        collection.add_book("Neuromancer", "William Gibson", "not-a-year")


def test_add_book_rejects_non_positive_year():
    collection = BookCollection()

    with pytest.raises(ValueError, match="Book year must be a positive integer"):
        collection.add_book("Neuromancer", "William Gibson", 0)


def test_find_by_year_range():
    collection = BookCollection()
    collection.add_book("Book One", "Author A", 1998)
    collection.add_book("Book Two", "Author B", 2005)
    collection.add_book("Book Three", "Author C", 2010)

    results = collection.find_by_year_range(2000, 2010)

    assert [book.title for book in results] == ["Book Two", "Book Three"]


def test_find_by_year_range_rejects_invalid_range():
    collection = BookCollection()

    with pytest.raises(ValueError, match="Start year cannot be greater than end year"):
        collection.find_by_year_range(2020, 2010)


def test_save_books_reports_write_failures(monkeypatch):
    collection = BookCollection()

    def fake_open(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(books.Path, "open", fake_open)

    with pytest.raises(RuntimeError, match="Unable to save books"):
        collection.save_books()
