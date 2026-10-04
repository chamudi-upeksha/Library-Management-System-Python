import sqlite3
import os
from datetime import datetime
import hashlib

DB_NAME = 'library.db'

def get_connection():
    return sqlite3.connect(DB_NAME)

def setup_database():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Books Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Books (
        BookID INTEGER PRIMARY KEY AUTOINCREMENT,
        Title TEXT NOT NULL,
        Author TEXT NOT NULL,
        Category TEXT,
        Publisher TEXT,
        ISBN TEXT,
        Quantity INTEGER NOT NULL,
        AvailableCopies INTEGER NOT NULL,
        ShelfLocation TEXT
    )
    ''')
    
    # Try adding ShelfLocation if it doesn't exist (for existing databases)
    try:
        cursor.execute("ALTER TABLE Books ADD COLUMN ShelfLocation TEXT")
    except sqlite3.OperationalError:
        pass

    # 2. Members Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Members (
        MemberID INTEGER PRIMARY KEY AUTOINCREMENT,
        FullName TEXT NOT NULL,
        Email TEXT,
        Phone TEXT,
        Address TEXT,
        MembershipType TEXT,
        JoinDate TEXT,
        Status TEXT DEFAULT 'Active'
    )
    ''')

    # 3. Borrowing Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Borrowing (
        BorrowID INTEGER PRIMARY KEY AUTOINCREMENT,
        MemberID INTEGER,
        BookID INTEGER,
        BorrowDate TEXT,
        ExpectedReturnDate TEXT,
        ActualReturnDate TEXT,
        Status TEXT,
        FOREIGN KEY(MemberID) REFERENCES Members(MemberID),
        FOREIGN KEY(BookID) REFERENCES Books(BookID)
    )
    ''')

    # 4. Fines Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Fines (
        FineID INTEGER PRIMARY KEY AUTOINCREMENT,
        BorrowID INTEGER,
        MemberID INTEGER,
        Amount REAL,
        PaidStatus TEXT DEFAULT 'Unpaid',
        Date TEXT,
        FOREIGN KEY(BorrowID) REFERENCES Borrowing(BorrowID),
        FOREIGN KEY(MemberID) REFERENCES Members(MemberID)
    )
    ''')

    # 5. Users Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        UserID INTEGER PRIMARY KEY AUTOINCREMENT,
        Username TEXT UNIQUE NOT NULL,
        Password TEXT NOT NULL,
        Role TEXT NOT NULL,
        LastLogin TEXT
    )
    ''')

    # 6. Categories Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Categories (
        CategoryID INTEGER PRIMARY KEY AUTOINCREMENT,
        CategoryName TEXT NOT NULL,
        Description TEXT
    )
    ''')

    # 7. Reservations Table (NEW)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Reservations (
        ReserveID INTEGER PRIMARY KEY AUTOINCREMENT,
        MemberID INTEGER,
        BookID INTEGER,
        ReserveDate TEXT,
        Status TEXT DEFAULT 'Pending',
        FOREIGN KEY(MemberID) REFERENCES Members(MemberID),
        FOREIGN KEY(BookID) REFERENCES Books(BookID)
    )
    ''')

    # 8. Audit Logs Table (NEW)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS AuditLogs (
        LogID INTEGER PRIMARY KEY AUTOINCREMENT,
        Username TEXT,
        Action TEXT,
        Details TEXT,
        Date TEXT
    )
    ''')

    # Insert default admin user if no users exist
    cursor.execute("SELECT COUNT(*) FROM Users")
    if cursor.fetchone()[0] == 0:
        hashed_pw = hashlib.sha256("admin".encode()).hexdigest()
        cursor.execute("INSERT INTO Users (Username, Password, Role) VALUES (?, ?, ?)",
                       ("admin", hashed_pw, "Admin"))

    conn.commit()
    conn.close()

def log_audit(username, action, details=""):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO AuditLogs (Username, Action, Details, Date) VALUES (?, ?, ?, ?)", 
                       (username, action, details, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
    except Exception as e:
        print("Audit log failed:", e)

if __name__ == "__main__":
    setup_database()
    print("Database setup complete with new features.")
