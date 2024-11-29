import pyodbc


def get_connection():
    """Establish and return a connection to the SQL Server database."""
    try:
        return pyodbc.connect(
            "DRIVER={SQL Server};"
            "SERVER=HOME_PC\\SQLEXPRESS;"  # Update to your SQL Server
            "DATABASE=Books;"  # Ensure this matches the database name
            "Trusted_Connection=yes;"
        )
    except pyodbc.Error as e:
        print("Error connecting to the database:", e)
        exit()


def create_table():
    """Create the `myBooks` table if it doesn't already exist."""
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='myBooks' AND xtype='U')
            BEGIN
                CREATE TABLE myBooks (
                    id INT PRIMARY KEY IDENTITY(1,1),
                    name NVARCHAR(100) NOT NULL,
                    author NVARCHAR(100) NOT NULL,
                    [read] BIT NOT NULL,
                    normalized_name AS LOWER(name) PERSISTED,
                    normalized_author AS LOWER(author) PERSISTED,
                    CONSTRAINT UC_Book_CaseInsensitive UNIQUE (normalized_name, normalized_author)
                )
            END
            """
        )
        connection.commit()
        print("Table `myBooks` ensured to exist.")
    except pyodbc.Error as e:
        print("Error creating table:", e)
    finally:
        connection.close()



def add_book(name, author):
    """Add a new book to the database, ensuring no duplicates."""
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO myBooks (name, author, [read]) VALUES (?, ?, 0)", (name, author)
        )
        connection.commit()
        print(f"Book '{name}' by {author} added to the database.")
    except pyodbc.IntegrityError:
        print(f"Book '{name}' by {author} already exists in the database.")
    except pyodbc.Error as e:
        print("Error adding book:", e)
    finally:
        connection.close()



def get_all_books():
    """Retrieve all books from the database."""
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT name, author, [read] FROM myBooks")
        books = [
            {"name": row[0], "author": row[1], "read": bool(row[2])}
            for row in cursor.fetchall()
        ]
        return books
    except pyodbc.Error as e:
        print("Error retrieving books:", e)
        return []
    finally:
        connection.close()


def mark_book_as_read(name):
    """Mark a book as read in the database (case-insensitive)."""
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("UPDATE myBooks SET [read] = 1 WHERE LOWER(name) = LOWER(?)", (name,))
        if cursor.rowcount > 0:
            print(f"Book '{name}' marked as read.")
        else:
            print(f"No book named '{name}' found.")
        connection.commit()
    finally:
        connection.close()


def delete_book(name):
    """Delete a book from the database (case-insensitive)."""
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM myBooks WHERE LOWER(name) = LOWER(?)", (name,))
        if cursor.rowcount > 0:
            print(f"Book '{name}' deleted.")
        else:
            print(f"No book named '{name}' found.")
        connection.commit()
    finally:
        connection.close()
