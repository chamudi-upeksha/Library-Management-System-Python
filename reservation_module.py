import tkinter as tk
from tkinter import ttk, messagebox
import database
from datetime import datetime

class ReservationFrame(ttk.Frame):
    def __init__(self, parent, username):
        super().__init__(parent)
        self.username = username
        self.create_widgets()
        self.load_data()
        
    def create_widgets(self):
        container = tk.Frame(self, bg="#FFFFFF", highlightbackground="#1E3A5F", highlightthickness=1)
        container.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(container, text="📅 Book Reservations", font=('Segoe UI', 14, 'bold'), fg="#1E3A5F", bg="#FFFFFF").grid(row=0, column=0, columnspan=4, pady=(10,5), padx=15, sticky="w")
        tk.Label(container, text="Place holds on unavailable books so members are notified when returned.", font=('Segoe UI', 9), fg="#64748B", bg="#FFFFFF").grid(row=1, column=0, columnspan=4, padx=15, sticky="w", pady=(0, 10))
        
        # Fields
        tk.Label(container, text="Member ID:", bg="#FFFFFF", fg="#172033").grid(row=2, column=0, padx=15, pady=5, sticky="e")
        self.txt_member_id = ttk.Entry(container, width=25)
        self.txt_member_id.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Label(container, text="Book ID:", bg="#FFFFFF", fg="#172033").grid(row=2, column=2, padx=15, pady=5, sticky="e")
        self.txt_book_id = ttk.Entry(container, width=25)
        self.txt_book_id.grid(row=2, column=3, padx=5, pady=5)
        
        # Buttons
        btn_frame = tk.Frame(container, bg="#FFFFFF")
        btn_frame.grid(row=3, column=0, columnspan=4, pady=15)
        
        ttk.Button(btn_frame, text="Reserve Book", width=15, command=self.add_reservation).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Fulfill (Complete)", width=15, style='Secondary.TButton', command=self.complete_reservation).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Cancel Hold", width=15, command=self.cancel_reservation).pack(side=tk.LEFT, padx=10)
        
        # Grid/Treeview
        tree_frame = tk.Frame(self, bg="#FFFFFF", highlightbackground="#1E3A5F", highlightthickness=1)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(tree_frame, text="Active Reservations Queue", font=('Segoe UI', 11, 'bold'), fg="#1E3A5F", bg="#FFFFFF").pack(anchor="w", padx=15, pady=10)
        
        columns = ("Reserve ID", "Member ID", "Book ID", "Book Title", "Date", "Status")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
            
        self.tree.column("Book Title", width=200)
            
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(15,0), pady=(0,15))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0,15), padx=(0,15))
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.selected_id = None
        
    def add_reservation(self):
        member_id = self.txt_member_id.get()
        book_id = self.txt_book_id.get()
        
        if not member_id or not book_id:
            messagebox.showerror("Error", "Member ID and Book ID are required.")
            return
            
        conn = database.get_connection()
        cursor = conn.cursor()
        
        # Verify Book
        cursor.execute("SELECT Title, AvailableCopies FROM Books WHERE BookID=?", (book_id,))
        book = cursor.fetchone()
        if not book:
            messagebox.showerror("Error", "Book not found.")
            conn.close()
            return
        
        if book[1] > 0:
            if not messagebox.askyesno("Info", "This book is currently available. Do you still want to place a hold?"):
                conn.close()
                return
                
        # Verify Member
        cursor.execute("SELECT Status FROM Members WHERE MemberID=?", (member_id,))
        member = cursor.fetchone()
        if not member or member[0] != 'Active':
            messagebox.showerror("Error", "Member not found or inactive.")
            conn.close()
            return
            
        reserve_date = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("INSERT INTO Reservations (MemberID, BookID, ReserveDate, Status) VALUES (?, ?, ?, 'Pending')",
                       (member_id, book_id, reserve_date))
        conn.commit()
        conn.close()
        
        database.log_audit(self.username, "Added Reservation", f"Member {member_id} reserved Book {book_id}")
        messagebox.showinfo("Success", "Reservation placed successfully!")
        self.load_data()
        
    def complete_reservation(self):
        if not self.selected_id:
            messagebox.showerror("Error", "Select a reservation first.")
            return
        
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Reservations SET Status='Fulfilled' WHERE ReserveID=?", (self.selected_id,))
        conn.commit()
        conn.close()
        
        database.log_audit(self.username, "Fulfilled Reservation", f"ReserveID {self.selected_id}")
        messagebox.showinfo("Success", "Reservation marked as fulfilled! You may now issue the book in Borrow/Return.")
        self.load_data()

    def cancel_reservation(self):
        if not self.selected_id:
            messagebox.showerror("Error", "Select a reservation first.")
            return
            
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Reservations SET Status='Cancelled' WHERE ReserveID=?", (self.selected_id,))
        conn.commit()
        conn.close()
        
        database.log_audit(self.username, "Cancelled Reservation", f"ReserveID {self.selected_id}")
        messagebox.showinfo("Success", "Reservation cancelled.")
        self.load_data()
        
    def load_data(self):
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute('''SELECT r.ReserveID, r.MemberID, r.BookID, b.Title, r.ReserveDate, r.Status 
                          FROM Reservations r
                          JOIN Books b ON r.BookID = b.BookID
                          WHERE r.Status = 'Pending' ''')
        rows = cursor.fetchall()
        conn.close()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert("", tk.END, values=row)
            
    def on_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            row = self.tree.item(selected_item[0])['values']
            self.selected_id = row[0]
            self.txt_member_id.delete(0, tk.END)
            self.txt_member_id.insert(0, row[1])
            self.txt_book_id.delete(0, tk.END)
            self.txt_book_id.insert(0, row[2])
