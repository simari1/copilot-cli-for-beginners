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


@pytest.mark.parametrize("start,end", [
    (1990.5, 2000),
    (1990, 2000.5),
    (1990.0, 2000.0),
])
def test_find_by_year_range_float_inputs_raise(start, end):
    collection = BookCollection()
    with pytest.raises(ValueError):
        collection.find_by_year_range(start, end)  # type: ignore


def test_find_by_year_range_second_arg_invalid():
    collection = BookCollection()
    with pytest.raises(ValueError):
        collection.find_by_year_range(1990, None)  # type: ignore


def test_find_by_year_range_bool_inputs_raise():
    """bool is a subclass of int in Python, so isinstance(True, int) is True.
    The implementation explicitly rejects booleans to prevent year=1/year=0 misuse."""
    collection = BookCollection()
    with pytest.raises(ValueError):
        collection.find_by_year_range(True, False)  # type: ignore


def test_find_by_year_range_excludes_outside_boundaries():
    collection = BookCollection()
    collection.add_book("Too Early", "Author A", 1989)
    collection.add_book("In Range", "Author B", 1990)
    collection.add_book("Too Late", "Author C", 2001)

    res = collection.find_by_year_range(1990, 2000)
    titles = [b.title for b in res]
    assert "In Range" in titles
    assert "Too Early" not in titles
    assert "Too Late" not in titles


def test_find_by_year_range_multiple_books_same_year():
    collection = BookCollection()
    collection.add_book("Book Alpha", "Author A", 2000)
    collection.add_book("Book Beta", "Author B", 2000)
    collection.add_book("Book Gamma", "Author C", 2000)

    res = collection.find_by_year_range(2000, 2000)
    assert len(res) == 3
    assert all(b.year == 2000 for b in res)


# --- add_book validation ---

def test_add_book_empty_title_raises():
    collection = BookCollection()
    with pytest.raises(ValueError):
        collection.add_book("", "Author", 2000)


def test_add_book_none_title_raises():
    collection = BookCollection()
    with pytest.raises(ValueError):
        collection.add_book(None, "Author", 2000)  # type: ignore


def test_add_book_empty_author_raises():
    collection = BookCollection()
    with pytest.raises(ValueError):
        collection.add_book("Title", "", 2000)


def test_add_book_none_author_raises():
    collection = BookCollection()
    with pytest.raises(ValueError):
        collection.add_book("Title", None, 2000)  # type: ignore


def test_add_book_string_year_raises():
    collection = BookCollection()
    with pytest.raises(ValueError):
        collection.add_book("Title", "Author", "2000")  # type: ignore


def test_add_book_float_year_raises():
    collection = BookCollection()
    with pytest.raises(ValueError):
        collection.add_book("Title", "Author", 1999.5)  # type: ignore


# --- list_books ---

def test_list_books_empty():
    collection = BookCollection()
    assert collection.list_books() == []


def test_list_books_returns_added_books():
    collection = BookCollection()
    collection.add_book("Book One", "Author A", 2000)
    collection.add_book("Book Two", "Author B", 2010)
    result = collection.list_books()
    assert len(result) == 2
    titles = [b.title for b in result]
    assert "Book One" in titles
    assert "Book Two" in titles


# --- mark_as_read ---

def test_mark_as_read_success():
    collection = BookCollection()
    collection.add_book("Read Me", "Author", 2020)
    result = collection.mark_as_read("Read Me")
    assert result is True
    book = collection.find_book_by_title("Read Me")
    assert book.read is True


def test_mark_as_read_not_found():
    collection = BookCollection()
    result = collection.mark_as_read("Nonexistent Book")
    assert result is False


# --- find_by_author ---

def test_find_by_author_match():
    collection = BookCollection()
    collection.add_book("Book A", "Jane Doe", 2000)
    collection.add_book("Book B", "John Smith", 2005)
    collection.add_book("Book C", "Jane Doe", 2010)
    results = collection.find_by_author("Jane Doe")
    assert len(results) == 2
    assert all(b.author == "Jane Doe" for b in results)


def test_find_by_author_no_match():
    collection = BookCollection()
    collection.add_book("Book A", "Someone Else", 2000)
    assert collection.find_by_author("Unknown Author") == []


def test_find_by_author_case_insensitive():
    collection = BookCollection()
    collection.add_book("A Book", "Jane Doe", 2000)
    results = collection.find_by_author("jane doe")
    assert len(results) == 1


def test_find_by_author_invalid_input():
    collection = BookCollection()
    assert collection.find_by_author(None) == []  # type: ignore


# --- find_similar_titles ---

def test_find_similar_titles_query_in_title():
    collection = BookCollection()
    collection.add_book("The Hitchhiker's Guide to the Galaxy", "Douglas Adams", 1979)
    results = collection.find_similar_titles("Hitchhiker")
    assert len(results) == 1


def test_find_similar_titles_no_match():
    collection = BookCollection()
    collection.add_book("Something Else", "Author", 2000)
    assert collection.find_similar_titles("Completely Unrelated Query") == []


def test_find_similar_titles_invalid_input():
    collection = BookCollection()
    assert collection.find_similar_titles(None) == []  # type: ignore


# --- get_statistics ---

def test_get_statistics_empty_collection():
    collection = BookCollection()
    stats = collection.get_statistics()
    assert stats["total_count"] == 0
    assert stats["read_count"] == 0
    assert stats["unread_count"] == 0
    assert stats["oldest_book"] is None
    assert stats["newest_book"] is None


def test_get_statistics_with_books():
    collection = BookCollection()
    collection.add_book("Old Book", "Author A", 1900)
    collection.add_book("New Book", "Author B", 2020)
    collection.add_book("Middle Book", "Author C", 1960)
    collection.mark_as_read("Old Book")
    stats = collection.get_statistics()
    assert stats["total_count"] == 3
    assert stats["read_count"] == 1
    assert stats["unread_count"] == 2
    assert stats["oldest_book"].year == 1900
    assert stats["newest_book"].year == 2020
