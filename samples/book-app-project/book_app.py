import sys
from books import BookCollection


# Global collection instance
collection = BookCollection()


def show_books(books):
    """Display books in a user-friendly format."""
    if not books:
        print("No books found.")
        return

    print("\nYour Book Collection:\n")

    for index, book in enumerate(books, start=1):
        status = "✓" if book.read else " "
        print(f"{index}. [{status}] {book.title} by {book.author} ({book.year})")

    print()


def handle_list():
    books = collection.list_books()
    show_books(books)


def handle_add():
    print("\nAdd a New Book\n")

    title = input("Title: ").strip()
    author = input("Author: ").strip()
    year_str = input("Year: ").strip()

    try:
        collection.add_book(title, author, year_str)
        print("\nBook added successfully.\n")
    except ValueError as e:
        print(f"\nError: {e}\n")
    except RuntimeError as e:
        print(f"\nError: {e}\n")


def handle_remove():
    print("\nRemove a Book\n")

    title = input("Enter the title of the book to remove: ").strip()
    if not title:
        print("\nError: title cannot be empty.\n")
        return

    try:
        removed = collection.remove_book(title)
    except RuntimeError as e:
        print(f"\nError: {e}\n")
        return

    if removed:
        print("\nBook removed.\n")
    else:
        print("\nBook not found.\n")


def handle_find():
    print("\nFind Books by Author\n")

    author = input("Author name: ").strip()
    if not author:
        print("\nError: author name cannot be empty.\n")
        return

    books = collection.find_by_author(author)

    show_books(books)


def handle_find_year_range():
    print("\nFind Books by Year Range\n")

    start_year = input("Start year: ").strip()
    end_year = input("End year: ").strip()

    try:
        books = collection.find_by_year_range(start_year, end_year)
    except ValueError as e:
        print(f"\nError: {e}\n")
        return

    show_books(books)


def show_help():
    print("""
Book Collection Helper

Commands:
  list     - Show all books
  add      - Add a new book
  remove   - Remove a book by title
  find     - Find books by author
  find-year - Find books published within a year range
  help     - Show this help message
""")


def main():
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    if command == "list":
        handle_list()
    elif command == "add":
        handle_add()
    elif command == "remove":
        handle_remove()
    elif command == "find":
        handle_find()
    elif command in {"find-year", "search-year", "year-range"}:
        handle_find_year_range()
    elif command == "help":
        show_help()
    else:
        print("Unknown command.\n")
        show_help()


if __name__ == "__main__":
    main()
