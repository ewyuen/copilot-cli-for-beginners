import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional

DATA_FILE = Path("data.json")


@dataclass
class Book:
    title: str
    author: str
    year: int
    read: bool = False


class BookCollection:
    def __init__(self):
        self.books: List[Book] = []
        self.load_books()

    @staticmethod
    def _data_path() -> Path:
        return Path(DATA_FILE)

    @staticmethod
    def _normalize_text(value, field_name: str, *, allow_empty: bool = True) -> str:
        if not isinstance(value, str):
            raise ValueError(f"{field_name} must be a string.")

        cleaned = value.strip()
        if not allow_empty and not cleaned:
            raise ValueError(f"{field_name} cannot be empty.")

        return cleaned

    @staticmethod
    def _normalize_year(value, field_name: str = "Book year") -> int:
        try:
            year = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{field_name} must be an integer.") from exc

        if year <= 0:
            raise ValueError(f"{field_name} must be a positive integer.")

        return year

    @classmethod
    def _coerce_book(cls, record) -> Book:
        if not isinstance(record, dict):
            raise ValueError("Book record must be a JSON object.")

        title = cls._normalize_text(record.get("title"), "Book title", allow_empty=False)
        author = cls._normalize_text(record.get("author", ""), "Book author")
        try:
            year_value = record["year"]
        except KeyError as exc:
            raise ValueError("Book year must be an integer.") from exc

        year = cls._normalize_year(year_value)

        read = bool(record.get("read", False))
        return Book(title=title, author=author, year=year, read=read)

    def load_books(self):
        """Load books from the JSON file if it exists."""
        try:
            with self._data_path().open("r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            self.books = []
            return
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Warning: could not load books from {DATA_FILE}: {exc}")
            self.books = []
            return

        if not isinstance(data, list):
            print(f"Warning: {DATA_FILE} should contain a list of books. Starting empty.")
            self.books = []
            return

        loaded_books: List[Book] = []
        for record in data:
            try:
                loaded_books.append(self._coerce_book(record))
            except ValueError as exc:
                print(f"Warning: skipping invalid book entry: {exc}")

        self.books = loaded_books

    def save_books(self):
        """Save the current book collection to JSON."""
        try:
            with self._data_path().open("w", encoding="utf-8") as f:
                json.dump([asdict(b) for b in self.books], f, indent=2)
        except OSError as exc:
            raise RuntimeError(f"Unable to save books to {DATA_FILE}: {exc}") from exc

    def add_book(self, title: str, author: str, year: int | str) -> Book:
        normalized_title = self._normalize_text(title, "Book title", allow_empty=False)
        normalized_author = self._normalize_text(author, "Book author")
        normalized_year = self._normalize_year(year)

        book = Book(title=normalized_title, author=normalized_author, year=normalized_year)
        self.books.append(book)
        try:
            self.save_books()
        except RuntimeError:
            self.books.pop()
            raise
        return book

    def list_books(self) -> List[Book]:
        return self.books

    def find_book_by_title(self, title: str) -> Optional[Book]:
        if not isinstance(title, str):
            return None

        cleaned_title = title.strip()
        if not cleaned_title:
            return None

        for book in self.books:
            if book.title.lower() == cleaned_title.lower():
                return book
        return None

    def mark_as_read(self, title: str) -> bool:
        book = self.find_book_by_title(title)
        if book:
            book.read = True
            self.save_books()
            return True
        return False

    def remove_book(self, title: str) -> bool:
        """Remove a book by title."""
        book = self.find_book_by_title(title)
        if book:
            self.books.remove(book)
            self.save_books()
            return True
        return False

    def find_by_author(self, author: str) -> List[Book]:
        """Find all books by a given author."""
        if not isinstance(author, str):
            return []

        cleaned_author = author.strip()
        if not cleaned_author:
            return []

        return [b for b in self.books if b.author.lower() == cleaned_author.lower()]

    def find_by_year_range(self, start_year: int | str, end_year: int | str) -> List[Book]:
        """Find books published within an inclusive year range."""
        start = self._normalize_year(start_year, "Start year")
        end = self._normalize_year(end_year, "End year")

        if start > end:
            raise ValueError("Start year cannot be greater than end year.")

        return [book for book in self.books if start <= book.year <= end]
