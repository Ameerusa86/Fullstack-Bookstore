import pyodbc
import logging

logging.basicConfig(level=logging.INFO)

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
        # Insert the book into the database
        cursor.execute(
            "INSERT INTO myBooks (name, author, [read]) VALUES (?, ?, 0)", (name, author)
        )
        connection.commit()
        return {"message": f"Book '{name}' by {author} added to the database."}
    except pyodbc.IntegrityError:
        return {"error": f"Book '{name}' by {author} already exists in the database."}
    except pyodbc.Error as e:
        return {"error": f"Database error: {str(e)}"}
    finally:
        connection.close()




def get_all_books():
    """Retrieve all books from the database."""
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT id, name, author, [read] FROM myBooks")
        books = [
            {
                "id": row[0],  # Include the id field
                "name": row[1],
                "author": row[2],
                "read": bool(row[3]),  # Convert BIT to bool
            }
            for row in cursor.fetchall()
        ]
        return books
    except pyodbc.Error as e:
        print("Error retrieving books:", e)
        return {"error": "Error fetching books."}
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


def delete_book(book_id):
    """Delete a book from the database by ID."""
    connection = get_connection()
    cursor = connection.cursor()
    try:
        logging.info(f"Attempting to delete book with ID: {book_id}")
        cursor.execute("DELETE FROM myBooks WHERE id = ?", (book_id,))
        if cursor.rowcount > 0:
            connection.commit()
            logging.info(f"Book with ID {book_id} successfully deleted.")
            return {"message": f"Book with ID {book_id} deleted from the database."}
        else:
            logging.warning(f"No book found with ID {book_id}.")
            return {"error": f"No book found with ID {book_id}."}
    except pyodbc.Error as e:
        logging.error(f"Database error: {str(e)}")
        return {"error": f"Database error: {str(e)}"}
    finally:
        connection.close()


def update_book(book_id, updates):
    """Update a book's details (name, author, and/or read status)."""
    connection = get_connection()
    cursor = connection.cursor()
    try:
        set_clauses = []
        params = []

        if "name" in updates:
            set_clauses.append("name = ?")
            params.append(updates["name"])
        if "author" in updates:
            set_clauses.append("author = ?")
            params.append(updates["author"])
        if "read" in updates:
            set_clauses.append("[read] = ?")
            params.append(updates["read"])

        if not set_clauses:
            logging.warning("No valid fields to update.")
            return {"error": "No valid fields to update."}

        params.append(book_id)
        query = f"UPDATE myBooks SET {', '.join(set_clauses)} WHERE id = ?"
        logging.info(f"Executing query: {query} with params: {params}")
        cursor.execute(query, params)

        if cursor.rowcount == 0:
            logging.warning(f"No book found with ID {book_id}.")
            return {"error": f"No book found with ID {book_id}."}

        connection.commit()
        logging.info(f"Book with ID {book_id} updated successfully.")
        return {"message": f"Book with ID {book_id} updated successfully."}
    except pyodbc.Error as e:
        logging.error(f"Database error: {str(e)}")
        return {"error": f"Database error: {str(e)}"}
    finally:
        connection.close()


