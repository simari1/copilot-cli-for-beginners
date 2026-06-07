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


def test_remove_book_exact_single():
    collection = BookCollection()
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
    result = collection.remove_book("The Hobbit")
    assert isinstance(result, dict)
    assert result["success"] is True
    assert result["removed"] == 1
    assert "Removed book" in result["message"]
    assert collection.find_book_by_title("The Hobbit") is None


def test_remove_book_invalid_title_input():
    collection = BookCollection()
    res_empty = collection.remove_book("")
    assert res_empty["success"] is False
    assert res_empty["removed"] == 0
    assert "Invalid title" in res_empty["message"]

    res_none = collection.remove_book(None)  # type: ignore
    assert res_none["success"] is False
    assert res_none["removed"] == 0
    assert "Invalid title" in res_none["message"]


def test_remove_book_no_match():
    collection = BookCollection()
    result = collection.remove_book("Nonexistent Book")
    assert result["success"] is False
    assert result["removed"] == 0
    assert "No book found" in result["message"]


def test_remove_book_multiple_exact_requires_index():
    collection = BookCollection()
    # Add two books with the same title
    collection.add_book("Hamlet", "Author A", 1600)
    collection.add_book("Hamlet", "Author B", 1610)

    # Calling without index should return ambiguity
    res = collection.remove_book("Hamlet")
    assert res["success"] is False
    assert res["removed"] == 0
    assert "Multiple books" in res["message"]
    assert isinstance(res.get("matches"), list)
    assert len(res["matches"]) == 2

    # Removing the second book by index
    res2 = collection.remove_book("Hamlet", index=2)
    assert res2["success"] is True
    assert res2["removed"] == 1
    assert "Removed book" in res2["message"]

    # One remaining match
    remaining = collection.find_books_by_title("Hamlet")
    assert len(remaining) == 1
    assert remaining[0].author == "Author A"


def test_remove_book_index_out_of_range_for_exact():
    collection = BookCollection()
    collection.add_book("Hamlet", "Author A", 1600)
    collection.add_book("Hamlet", "Author B", 1610)
    res = collection.remove_book("Hamlet", index=3)
    assert res["success"] is False
    assert res["removed"] == 0
    assert "Index out of range for exact matches" in res["message"]
    assert isinstance(res.get("matches"), list)


def test_remove_book_similar_and_remove_by_index():
    collection = BookCollection()
    collection.add_book("The Hitchhiker's Guide to the Galaxy", "Douglas Adams", 1979)

    # No exact match, but similar titles should be returned
    res = collection.remove_book("Hitchhiker")
    assert res["success"] is False
    assert res["removed"] == 0
    assert "Similar titles" in res["message"] or "similar" in res
    assert isinstance(res.get("similar"), list)
    assert len(res["similar"]) >= 1

    # Remove by index from similar
    res2 = collection.remove_book("Hitchhiker", index=1)
    assert res2["success"] is True
    assert res2["removed"] == 1
    assert "Removed book" in res2["message"]
    assert collection.find_book_by_title("The Hitchhiker's Guide to the Galaxy") is None


def test_remove_book_index_out_of_range_for_similar():
    collection = BookCollection()
    collection.add_book("Similar Title", "Author X", 2000)
    res = collection.remove_book("Similar", index=99)
    assert res["success"] is False
    assert res["removed"] == 0
    assert "Index out of range for similar titles" in res["message"]
    assert isinstance(res.get("similar"), list)


def test_find_by_year_range_inclusive_boundaries():
    collection = BookCollection()
    collection.add_book("Book A", "Author A", 1990)
    collection.add_book("Book B", "Author B", 1995)
    collection.add_book("Book C", "Author C", 2000)

    res = collection.find_by_year_range(1990, 2000)
    assert isinstance(res, list)
    assert len(res) == 3
    years = sorted(b.year for b in res)
    assert years == [1990, 1995, 2000]


def test_find_by_year_range_single_year():
    collection = BookCollection()
    collection.add_book("Only One", "Solo Author", 2020)

    res = collection.find_by_year_range(2020, 2020)
    assert len(res) == 1
    assert res[0].year == 2020


def test_find_by_year_range_reversed():
    collection = BookCollection()
    collection.add_book("Old", "Author X", 1980)
    collection.add_book("New", "Author Y", 1990)

    res_forward = collection.find_by_year_range(1980, 1990)
    res_reversed = collection.find_by_year_range(1990, 1980)
    assert sorted([b.title for b in res_forward]) == sorted([b.title for b in res_reversed])


def test_find_by_year_range_no_matches():
    collection = BookCollection()
    collection.add_book("Later Book", "Author Z", 2001)

    res = collection.find_by_year_range(1990, 2000)
    assert res == []


def test_find_by_year_range_empty_collection():
    collection = BookCollection()
    res = collection.find_by_year_range(1900, 1950)
    assert res == []


def test_find_by_year_range_invalid_inputs():
    collection = BookCollection()
    with pytest.raises(ValueError):
        collection.find_by_year_range("1990", "2000")
    with pytest.raises(ValueError):
        collection.find_by_year_range(None, 2000)  # type: ignore
