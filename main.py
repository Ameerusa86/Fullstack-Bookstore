from utils import database
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Ensure the table exists when the application starts
database.create_table()

USER_CHOICE = """
ENTER:
- 'a' to add a book
- 'l' to list all books
- 'r' to mark a book as read
- 'd' to delete a book
- 'q' to quit
Your choice:
"""


def menu():
    """Main menu loop to interact with the user."""
    user_input = input(USER_CHOICE)
    while user_input != "q":
        if user_input == "a":
            prompt_add_book()
        elif user_input == "l":
            list_books()
        elif user_input == "r":
            prompt_read_book()
        elif user_input == "d":
            prompt_delete_book()
        else:
            print("Unknown command. Please try again.")
        user_input = input(USER_CHOICE)


def prompt_add_book():
    name = input("Enter the name of the book: ").strip()
    author = input("Enter the author of the book: ").strip()
    database.add_book(name, author)


def list_books():
    books = database.get_all_books()
    if not books:
        print("No books found in the database.")
    else:
        for book in books:
            read = "YES" if book["read"] else "NO"
            print(f"{book['name']} by {book['author']}, read: {read}")


def prompt_read_book():
    name = input("Enter the name of the book you just finished reading: ").strip()
    database.mark_book_as_read(name)


def prompt_delete_book():
    name = input("Enter the name of the book you want to delete: ").strip()
    database.delete_book(name)


# FastAPI models
class Book(BaseModel):
    name: str
    author: str


@app.post("/books")
def add_book(book: Book):
    """Add a new book via API."""
    database.add_book(book.name, book.author)
    return {"message": f"Book '{book.name}' by {book.author} added."}


@app.get("/books", response_model=List[Book])
def get_books():
    """List all books via API."""
    return database.get_all_books()


@app.put("/books/{name}")
def mark_as_read(name: str):
    """Mark a book as read via API."""
    database.mark_book_as_read(name)
    return {"message": f"Book '{name}' marked as read."}


@app.delete("/books/{name}")
def delete_a_book(name: str):
    """Delete a book via API."""
    database.delete_book(name)
    return {"message": f"Book '{name}' deleted."}


if __name__ == "__main__":
    menu()