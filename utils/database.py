import pyodbc


def get_connection():
    """Establish and return a connection to the SQL Server database."""
    try:
        return pyodbc.connect(
            "DRIVER={SQL Server};"
            "SERVER=HOME_PC\\SQLEXPRESS;"  # Update with your server name
            "DATABASE=Books;"  # Ensure the database name matches
            "Trusted_Connection=yes;"
        )
    except pyodbc.Error as e:
        print("Error connecting to the database:", e)
        exit()


def create_table():
    """Create the `books` table if it doesn't already exist."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='books' AND xtype='U')
        CREATE TABLE books (
            id INT PRIMARY KEY IDENTITY(1,1),
            name NVARCHAR(100),
            author NVARCHAR(100),
            [read] BIT
        )
        """
    )
    connection.commit()
    connection.close()


def add_book(name, author):
    """Add a new book to the database."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO books (name, author, read) VALUES (?, ?, 0)", (name, author)
    )
    connection.commit()
    connection.close()
    print(f"Book '{name}' by {author} added to the database.")


def get_all_books():
    """Retrieve all books from the database."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT name, author, [read] FROM books")
    books = [
        {"name": row[0], "author": row[1], "read": bool(row[2])}
        for row in cursor.fetchall()
    ]
    connection.close()
    return books


def mark_book_as_read(name):
    """Mark a book as read in the database."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE books SET [read] = 1 WHERE name = ?", (name,))
    if cursor.rowcount == 0:
        print(f"No book named '{name}' found in the database.")
    else:
        print(f"Book '{name}' marked as read.")
    connection.commit()
    connection.close()


def delete_book(name):
    """Delete a book from the database."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM books WHERE name = ?", (name,))
    if cursor.rowcount == 0:
        print(f"No book named '{name}' found in the database.")
    else:
        print(f"Book '{name}' deleted from the database.")
    connection.commit()
    connection.close()
