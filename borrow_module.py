import tkinter as tk
from tkinter import ttk, messagebox
import database
from datetime import datetime, timedelta

class BorrowReturnFrame(ttk.Frame):
    def __init__(self, parent, username):
        super().__init__(parent)
        self.username = username
        self.create_widgets()
        self.load_data()
        
    def create_widgets(self):
        container = tk.Frame(self, bg="#FFFFFF", highlightbackground="#1E3A5F", highlightthickness=1)
        container.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(container, text="Borrow / Return Book", font=('Segoe UI', 14, 'bold'), fg="#1E3A5F", bg="#FFFFFF").grid(row=0, column=0, columnspan=4, pady=(10,5), padx=15, sticky="w")
        
        # Fields
        tk.Label(container, text="Member ID:", bg="#FFFFFF", fg="#172033").grid(row=1, column=0, padx=15, pady=10, sticky="e")
        self.txt_member_id = ttk.Entry(container, width=25)
        self.txt_member_id.grid(row=1, column=1, padx=5, pady=10)
        
        tk.Label(container, text="Book ID:", bg="#FFFFFF", fg="#172033").grid(row=1, column=2, padx=15, pady=10, sticky="e")
        self.txt_book_id = ttk.Entry(container, width=25)
        self.txt_book_id.grid(row=1, column=3, padx=5, pady=10)
        
        # Buttons
        btn_frame = tk.Frame(container, bg="#FFFFFF")
        btn_frame.grid(row=2, column=0, columnspan=4, pady=20)
        
        ttk.Button(btn_frame, text="Borrow Book", width=18, command=self.borrow_book).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Return Book", width=18, style='Secondary.TButton', command=self.return_book).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Clear", width=18, command=self.clear_fields).pack(side=tk.LEFT, padx=10)
        
        # Grid/Treeview for Borrowing History
        tree_frame = tk.Frame(self, bg="#FFFFFF", highlightbackground="#1E3A5F", highlightthickness=1)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(tree_frame, text="Currently Borrowed Books", font=('Segoe UI', 12, 'bold'), fg="#1E3A5F", bg="#FFFFFF").pack(anchor="w", padx=15, pady=10)
        
        columns = ("Borrow ID", "Member ID", "Book ID", "Borrow Date", "Expected Return", "Status")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
            
        self.tree.tag_configure('overdue', foreground="#EF4444")
        self.tree.tag_configure('duesoon', foreground="#F59E0B")
        self.tree.tag_configure('normal', foreground="#1E3A5F")
            
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(15,0), pady=(0,15))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0,15), padx=(0,15))
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.selected_borrow_id = None
        self.selected_book_id = None
        
    def borrow_book(self):
        member_id = self.txt_member_id.get()
        book_id = self.txt_book_id.get()
        
        if not member_id or not book_id:
            messagebox.showerror("Error", "Member ID and Book ID are required.")
            return
            
        conn = database.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT Status FROM Members WHERE MemberID=?", (member_id,))
        member = cursor.fetchone()
        if not member:
            messagebox.showerror("Error", "Member not found.")
            conn.close()
            return
        if member[0] != 'Active':
            messagebox.showerror("Error", "Member is not active.")
            conn.close()
            return
            
        cursor.execute("SELECT AvailableCopies FROM Books WHERE BookID=?", (book_id,))
        book = cursor.fetchone()
        if not book or book[0] <= 0:
            messagebox.showerror("Error", "Book is not available.")
            conn.close()
            return
            
        borrow_date = datetime.now().strftime("%Y-%m-%d")
        expected_return = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        
        cursor.execute("INSERT INTO Borrowing (MemberID, BookID, BorrowDate, ExpectedReturnDate, Status) VALUES (?, ?, ?, ?, ?)",
                       (member_id, book_id, borrow_date, expected_return, 'Borrowed'))
                       
        cursor.execute("UPDATE Books SET AvailableCopies = AvailableCopies - 1 WHERE BookID=?", (book_id,))
        
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", f"Book borrowed successfully.\nExpected Return Date: {expected_return}")
        self.clear_fields()
        self.load_data()
        
    def return_book(self):
        if not self.selected_borrow_id:
            messagebox.showerror("Error", "Please select a borrowing record from the list to return.")
            return
            
        return_date = datetime.now().strftime("%Y-%m-%d")
        
        conn = database.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT ExpectedReturnDate, MemberID FROM Borrowing WHERE BorrowID=?", (self.selected_borrow_id,))
        result = cursor.fetchone()
        if result:
            expected_date = datetime.strptime(result[0], "%Y-%m-%d")
            actual_date = datetime.now()
            
            if actual_date > expected_date:
                days_late = (actual_date - expected_date).days
                fine_amount = days_late * 0.50 # $0.50 per day
                cursor.execute("INSERT INTO Fines (BorrowID, MemberID, Amount, Date) VALUES (?, ?, ?, ?)",
                               (self.selected_borrow_id, result[1], fine_amount, return_date))
                messagebox.showwarning("Late Return", f"Book returned late! A fine of ${fine_amount:.2f} has been added.")
                
        cursor.execute("UPDATE Borrowing SET ActualReturnDate=?, Status='Returned' WHERE BorrowID=?", 
                       (return_date, self.selected_borrow_id))
                       
        cursor.execute("UPDATE Books SET AvailableCopies = AvailableCopies + 1 WHERE BookID=?", (self.selected_book_id,))
        
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Book returned successfully")
        self.clear_fields()
        self.load_data()
        
    def load_data(self):
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT BorrowID, MemberID, BookID, BorrowDate, ExpectedReturnDate, Status FROM Borrowing WHERE Status='Borrowed'")
        rows = cursor.fetchall()
        conn.close()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        current_date = datetime.now()
        for row in rows:
            expected_date = datetime.strptime(row[4], "%Y-%m-%d")
            days_until_due = (expected_date - current_date).days
            
            tag = 'normal'
            if days_until_due < 0:
                tag = 'overdue'
            elif days_until_due <= 3:
                tag = 'duesoon'
                
            self.tree.insert("", tk.END, values=row, tags=(tag,))
            
    def on_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            row = self.tree.item(selected_item[0])['values']
            self.selected_borrow_id = row[0]
            self.txt_member_id.delete(0, tk.END)
            self.txt_member_id.insert(0, row[1])
            self.txt_book_id.delete(0, tk.END)
            self.txt_book_id.insert(0, row[2])
            self.selected_book_id = row[2]
            
    def clear_fields(self):
        self.selected_borrow_id = None
        self.selected_book_id = None
        self.txt_member_id.delete(0, tk.END)
        self.txt_book_id.delete(0, tk.END)
