import json
import unicodedata
from dataclasses import dataclass, asdict
from typing import List, Optional

DATA_FILE = "data.json"


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

    def _normalize(self, s: str) -> str:
        """Normalize, strip and lowercase strings for reliable comparisons."""
        if not isinstance(s, str):
            return ""
        return unicodedata.normalize("NFC", s).strip().lower()

    def load_books(self):
        """Load books from the JSON file if it exists."""
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                self.books = [Book(**b) for b in data]
        except FileNotFoundError:
            self.books = []
        except json.JSONDecodeError:
            print("Warning: data.json is corrupted. Starting with empty collection.")
            self.books = []

    def save_books(self):
        """Save the current book collection to JSON."""
        with open(DATA_FILE, "w") as f:
            json.dump([asdict(b) for b in self.books], f, indent=2)

    def add_book(self, title: str, author: str, year: int) -> Book:
        book = Book(title=title, author=author, year=year)
        self.books.append(book)
        self.save_books()
        return book

    def list_books(self) -> List[Book]:
        return self.books

    def find_book_by_title(self, title: str) -> Optional[Book]:
        """Return the first exact (normalized) match for title, or None."""
        if not isinstance(title, str):
            return None
        norm = self._normalize(title)
        for book in self.books:
            if self._normalize(book.title) == norm:
                return book
        return None

    def find_books_by_title(self, title: str) -> List[Book]:
        """Return all exact (normalized) matches for title."""
        if not isinstance(title, str):
            return []
        norm = self._normalize(title)
        return [b for b in self.books if self._normalize(b.title) == norm]

    def find_similar_titles(self, title: str) -> List[Book]:
        """Return books where the normalized title contains the query or vice-versa (simple similarity)."""
        if not isinstance(title, str):
            return []
        norm = self._normalize(title)
        return [b for b in self.books if norm in self._normalize(b.title) or self._normalize(b.title) in norm]

    def mark_as_read(self, title: str) -> bool:
        book = self.find_book_by_title(title)
        if book:
            book.read = True
            self.save_books()
            return True
        return False

    def remove_book(self, title: str, index: Optional[int] = None) -> dict:
        """Remove a book by title or by index when multiple matches exist.

        Parameters:
        - title: the title to search for (string)
        - index: optional 1-based index into the matches/similar lists to disambiguate

        Returns a dict with keys:
        - success: bool
        - removed: int (number removed)
        - message: str
        - matches / similar: optional lists of titles when ambiguous or no exact match
        """
        # Basic validation
        if not isinstance(title, str) or not title.strip():
            return {"success": False, "removed": 0, "message": "Invalid title provided."}

        # Find exact matches first
        exact_matches = self.find_books_by_title(title)

        # If exact matches exist
        if exact_matches:
            # If an index was provided, attempt to remove that specific match
            if index is not None:
                if not isinstance(index, int) or index < 1 or index > len(exact_matches):
                    return {
                        "success": False,
                        "removed": 0,
                        "message": "Index out of range for exact matches.",
                        "matches": [b.title for b in exact_matches]
                    }
                book = exact_matches[index - 1]
                try:
                    self.books.remove(book)
                    self.save_books()
                    return {"success": True, "removed": 1, "message": f"Removed book: {book.title}"}
                except ValueError:
                    return {"success": False, "removed": 0, "message": "Failed to remove book (internal error)."}

            # No index: ambiguous if multiple
            if len(exact_matches) > 1:
                return {
                    "success": False,
                    "removed": 0,
                    "message": "Multiple books match that title. Provide an index to disambiguate.",
                    "matches": [b.title for b in exact_matches]
                }

            # Single exact match -> remove
            book = exact_matches[0]
            try:
                self.books.remove(book)
                self.save_books()
                return {"success": True, "removed": 1, "message": f"Removed book: {book.title}"}
            except ValueError:
                return {"success": False, "removed": 0, "message": "Failed to remove book (internal error)."}

        # No exact matches: look for similar titles
        similar = self.find_similar_titles(title)
        if similar:
            if index is not None:
                if not isinstance(index, int) or index < 1 or index > len(similar):
                    return {
                        "success": False,
                        "removed": 0,
                        "message": "Index out of range for similar titles.",
                        "similar": [b.title for b in similar]
                    }
                book = similar[index - 1]
                try:
                    self.books.remove(book)
                    self.save_books()
                    return {"success": True, "removed": 1, "message": f"Removed book: {book.title} (from similar matches)"}
                except ValueError:
                    return {"success": False, "removed": 0, "message": "Failed to remove book (internal error)."}

            return {
                "success": False,
                "removed": 0,
                "message": "No exact match found. Similar titles exist.",
                "similar": [b.title for b in similar]
            }

        return {"success": False, "removed": 0, "message": "No book found with that title."}

    def find_by_author(self, author: str) -> List[Book]:
        """Find all books by a given author."""
        return [b for b in self.books if b.author.lower() == author.lower()]

    def get_statistics(self) -> dict:
        """本の統計情報を取得します。"""
        if not self.books:
            return {
                "total_count": 0,
                "read_count": 0,
                "unread_count": 0,
                "oldest_book": None,
                "newest_book": None
            }
        
        read_count = sum(1 for book in self.books if book.read)
        unread_count = len(self.books) - read_count
        oldest_book = min(self.books, key=lambda b: b.year)
        newest_book = max(self.books, key=lambda b: b.year)
        
        return {
            "total_count": len(self.books),
            "read_count": read_count,
            "unread_count": unread_count,
            "oldest_book": oldest_book,
            "newest_book": newest_book
        }

    def find_by_year_range(self, start_year: int, end_year: int) -> List[Book]:
        """Find books published between start_year and end_year (inclusive).

        Validates inputs and accepts start_year > end_year by swapping values.
        Raises ValueError if either argument is not an int.
        Returns a list of Book instances matching the range.
        """
        if not isinstance(start_year, int) or not isinstance(end_year, int):
            raise ValueError("start_year and end_year must be integers")

        # Allow reversed ranges by swapping
        if start_year > end_year:
            start_year, end_year = end_year, start_year

        return [b for b in self.books if start_year <= b.year <= end_year]
