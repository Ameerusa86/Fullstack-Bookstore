from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from utils import database
# Initialize FastAPI
app = FastAPI()

# Ensure the table exists when the API starts
# database.create_table()


# Pydantic Models
class Book(BaseModel):
    name: str
    author: str


class BookResponse(Book):
    id: int
    read: bool

class UpdateBook(BaseModel):
    name: Optional[str] = None
    author: Optional[str] = None
    read: Optional[bool] = None


@app.get("/")
def root():
    """Root endpoint for the API."""
    return {"message": "Welcome to the Book Management API! Visit /docs for API documentation."}


@app.post("/books", status_code=201)
def create_book(book: Book):
    """Add a new book to the database."""
    result = database.add_book(book.name, book.author)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"message": f"Book '{book.name}' by {book.author} added."}



@app.get("/books", response_model=List[BookResponse])
def list_books():
    """Retrieve all books from the database."""
    result = database.get_all_books()
    if isinstance(result, list):  # Success
        return result
    raise HTTPException(status_code=500, detail="Error fetching books.")


@app.put("/books/{book_id}")
def update_book(book_id: int, book: UpdateBook):
    """Update book details: name, author, and/or read status."""
    updates = {}
    if book.name:
        updates["name"] = book.name
    if book.author:
        updates["author"] = book.author
    if book.read is not None:
        updates["read"] = 1 if book.read else 0

    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided for update.")

    result = database.update_book(book_id, updates)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return {"message": f"Book with ID {book_id} updated successfully."}



@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    """Delete a book from the database."""
    result = database.delete_book(book_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return {"message": f"Book with ID {book_id} deleted."}
