from utils import database
from utils.database import get_connection

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
    add_book(name, author)


def add_book(name, author):
    """Add a new book to the database."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO books (name, author, [read]) VALUES (?, ?, 0)", (name, author)
    )
    connection.commit()
    connection.close()
    print(f"Book '{name}' by {author} added to the database.")


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


if __name__ == "__main__":
    database.create_table()  # Ensure the table exists
    menu()
