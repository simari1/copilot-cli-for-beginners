"""
CLI entry point for the Book Collection app.

Provides a command-line interface for managing a personal book collection.
Delegates data operations to :class:`books.BookCollection`.

Usage::

    python book_app.py <command>

Commands:
    list       Show all books in the collection
    add        Interactively add a new book
    remove     Remove a book by title
    mark-read  Mark a book as read by title
    find       Search books by author name
    help       Show available commands
"""

import sys
from books import Book, BookCollection


# Global collection instance shared by all command handlers
collection: BookCollection = BookCollection()


def show_books(books: list[Book]) -> None:
    """Display a list of books in a numbered, human-readable format.

    Each entry shows a read status indicator (✓ or space), title, author,
    and publication year. Prints "No books found." when the list is empty.

    Args:
        books (list[Book]): Books to display. May be empty.
    """
    if not books:
        print("No books found.")
        return

    print("\nYour Book Collection:\n")

    for index, book in enumerate(books, start=1):
        status = "✓" if book.read else " "
        print(f"{index}. [{status}] {book.title} by {book.author} ({book.year})")

    print()


def handle_list() -> None:
    """Retrieve and display all books in the collection."""
    books = collection.list_books()
    show_books(books)


def handle_list_unread() -> None:
    """Retrieve and display only unread books in the collection."""
    books = collection.list_unread()
    show_books(books)


def handle_add() -> None:
    """Interactively prompt the user for book details and add the book.

    Prompts for title, author, and year. Year defaults to 0 if left blank.
    Prints an error message if the input is invalid (e.g. non-numeric year).
    """
    print("\nAdd a New Book\n")

    title = input("Title: ").strip()
    author = input("Author: ").strip()
    year_str = input("Year: ").strip()

    try:
        year = int(year_str) if year_str else 0
        collection.add_book(title, author, year)
        print("\nBook added successfully.\n")
    except ValueError as e:
        print(f"\nError: {e}\n")


def handle_remove() -> None:
    """Prompt the user for a title and remove the matching book.

    Silently succeeds if no book with the given title exists.
    """
    print("\nRemove a Book\n")

    title = input("Enter the title of the book to remove: ").strip()
    collection.remove_book(title)

    print("\nBook removed if it existed.\n")


def handle_find() -> None:
    """Prompt for an author name and display all matching books."""
    print("\nFind Books by Author\n")

    author = input("Author name: ").strip()
    books = collection.find_by_author(author)

    show_books(books)


def handle_mark_read() -> None:
    """Prompt for a title and mark the matching book as read.

    Prints a confirmation message on success, or a "not found" message
    if no book with that title exists in the collection.
    """
    print("\nMark a Book as Read\n")

    title = input("Enter the title of the book to mark as read: ").strip()
    
    if collection.mark_as_read(title):
        print(f"\n'{title}' marked as read.\n")
    else:
        print(f"\nBook '{title}' not found.\n")


def show_help() -> None:
    """Print a summary of all available CLI commands."""
    print("""
Book Collection Helper

Commands:
  list        - Show all books
  list-unread - Show only unread books
  add         - Add a new book
  remove   - Remove a book by title
  mark-read - Mark a book as read
  find     - Find books by author
  help     - Show this help message
""")


def main() -> None:
    """Parse the CLI argument and dispatch to the appropriate handler.

    Reads the first positional argument from ``sys.argv`` and calls the
    matching ``handle_*`` function. Shows help when no argument is given
    or the command is unrecognised.
    """
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    if command == "list":
        handle_list()
    elif command == "list-unread":
        handle_list_unread()
    elif command == "add":
        handle_add()
    elif command == "remove":
        handle_remove()
    elif command == "mark-read":
        handle_mark_read()
    elif command == "find":
        handle_find()
    elif command == "help":
        show_help()
    else:
        print("Unknown command.\n")
        show_help()


if __name__ == "__main__":
    main()
