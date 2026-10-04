import tkinter as tk
from tkinter import ttk, messagebox
import database

class BookManagementFrame(ttk.Frame):
    def __init__(self, parent, username):
        super().__init__(parent)
        self.username = username
        self.create_widgets()
        self.load_data()
        
    def create_widgets(self):
        container = tk.Frame(self, bg="#FFFFFF", highlightbackground="#1E3A5F", highlightthickness=1)
        container.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(container, text="📚 Manage Books", font=('Segoe UI', 14, 'bold'), fg="#1E3A5F", bg="#FFFFFF").grid(row=0, column=0, columnspan=4, pady=(10,5), padx=15, sticky="w")
        
        tk.Label(container, text="Title:", bg="#FFFFFF", fg="#172033").grid(row=1, column=0, padx=15, pady=5, sticky="e")
        self.txt_title = ttk.Entry(container, width=35)
        self.txt_title.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(container, text="Author:", bg="#FFFFFF", fg="#172033").grid(row=1, column=2, padx=15, pady=5, sticky="e")
        self.txt_author = ttk.Entry(container, width=35)
        self.txt_author.grid(row=1, column=3, padx=5, pady=5)
        
        tk.Label(container, text="Category:", bg="#FFFFFF", fg="#172033").grid(row=2, column=0, padx=15, pady=5, sticky="e")
        self.cmb_category = ttk.Combobox(container, values=["Fiction", "Non-Fiction", "Science", "History", "Technology", "Art", "Reference"], width=33)
        self.cmb_category.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Label(container, text="Publisher:", bg="#FFFFFF", fg="#172033").grid(row=2, column=2, padx=15, pady=5, sticky="e")
        self.txt_publisher = ttk.Entry(container, width=35)
        self.txt_publisher.grid(row=2, column=3, padx=5, pady=5)
        
        tk.Label(container, text="ISBN:", bg="#FFFFFF", fg="#172033").grid(row=3, column=0, padx=15, pady=5, sticky="e")
        self.txt_isbn = ttk.Entry(container, width=35)
        self.txt_isbn.grid(row=3, column=1, padx=5, pady=5)
        
        tk.Label(container, text="Quantity:", bg="#FFFFFF", fg="#172033").grid(row=3, column=2, padx=15, pady=5, sticky="e")
        self.txt_qty = ttk.Spinbox(container, from_=1, to=100, width=33)
        self.txt_qty.grid(row=3, column=3, padx=5, pady=5)
        
        tk.Label(container, text="Shelf Loc.:", bg="#FFFFFF", fg="#172033").grid(row=4, column=0, padx=15, pady=5, sticky="e")
        self.txt_location = ttk.Entry(container, width=35)
        self.txt_location.grid(row=4, column=1, padx=5, pady=5)
        
        btn_frame = tk.Frame(container, bg="#FFFFFF")
        btn_frame.grid(row=5, column=0, columnspan=4, pady=15)
        
        ttk.Button(btn_frame, text="Add Book", width=12, command=self.add_book).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Update Book", width=12, command=self.update_book).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Delete Book", width=12, command=self.delete_book).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Clear", width=12, style='Secondary.TButton', command=self.clear_fields).pack(side=tk.LEFT, padx=10)
        
        # ADVANCED SEARCH FRAME
        search_frame = tk.Frame(self, bg="#ECF0F5")
        search_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(search_frame, text="🔍 Advanced Search:", bg="#ECF0F5", fg="#172033", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, padx=5)
        
        tk.Label(search_frame, text="Title:", bg="#ECF0F5").grid(row=0, column=1, padx=2)
        self.search_title = ttk.Entry(search_frame, width=15)
        self.search_title.grid(row=0, column=2, padx=5)
        
        tk.Label(search_frame, text="Author:", bg="#ECF0F5").grid(row=0, column=3, padx=2)
        self.search_author = ttk.Entry(search_frame, width=15)
        self.search_author.grid(row=0, column=4, padx=5)
        
        tk.Label(search_frame, text="Category:", bg="#ECF0F5").grid(row=0, column=5, padx=2)
        self.search_category = ttk.Combobox(search_frame, values=["", "Fiction", "Non-Fiction", "Science", "History", "Technology"], width=12)
        self.search_category.grid(row=0, column=6, padx=5)
        
        ttk.Button(search_frame, text="Search", command=self.search_books).grid(row=0, column=7, padx=5)
        ttk.Button(search_frame, text="View All", style='Secondary.TButton', command=self.load_data).grid(row=0, column=8, padx=5)
        
        # Grid/Treeview
        tree_frame = tk.Frame(self, bg="#FFFFFF", highlightbackground="#1E3A5F", highlightthickness=1)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        columns = ("ID", "Title", "Author", "Category", "ISBN", "Total", "Available", "Location")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
            
        self.tree.column("ID", width=40)
        self.tree.column("Title", width=200)
        
        self.tree.tag_configure('available', foreground="#2A9D8F")
        self.tree.tag_configure('unavailable', foreground="#EF4444")
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.selected_id = None
        
    def add_book(self):
        title = self.txt_title.get()
        author = self.txt_author.get()
        category = self.cmb_category.get()
        pub = self.txt_publisher.get()
        isbn = self.txt_isbn.get()
        qty = self.txt_qty.get()
        loc = self.txt_location.get()
        
        if not title or not author or not qty:
            messagebox.showerror("Error", "Title, Author and Quantity are required.")
            return
            
        try:
            qty = int(qty)
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Books (Title, Author, Category, Publisher, ISBN, Quantity, AvailableCopies, ShelfLocation) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                           (title, author, category, pub, isbn, qty, qty, loc))
            conn.commit()
            conn.close()
            database.log_audit(self.username, "Added Book", f"Title: {title}")
            messagebox.showinfo("Success", "Book added successfully")
            self.clear_fields()
            self.load_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def update_book(self):
        if not self.selected_id:
            messagebox.showerror("Error", "Select a book to update")
            return
            
        title = self.txt_title.get()
        author = self.txt_author.get()
        category = self.cmb_category.get()
        pub = self.txt_publisher.get()
        isbn = self.txt_isbn.get()
        loc = self.txt_location.get()
        
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Books SET Title=?, Author=?, Category=?, Publisher=?, ISBN=?, ShelfLocation=? WHERE BookID=?",
                       (title, author, category, pub, isbn, loc, self.selected_id))
        conn.commit()
        conn.close()
        database.log_audit(self.username, "Updated Book", f"Book ID: {self.selected_id}")
        messagebox.showinfo("Success", "Book updated successfully")
        self.clear_fields()
        self.load_data()
        
    def delete_book(self):
        if not self.selected_id:
            messagebox.showerror("Error", "Select a book to delete")
            return
            
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this book?"):
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Books WHERE BookID=?", (self.selected_id,))
            conn.commit()
            conn.close()
            database.log_audit(self.username, "Deleted Book", f"Book ID: {self.selected_id}")
            messagebox.showinfo("Success", "Book deleted successfully")
            self.clear_fields()
            self.load_data()
            
    def search_books(self):
        title = f"%{self.search_title.get()}%"
        author = f"%{self.search_author.get()}%"
        category = f"%{self.search_category.get()}%"
        
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT BookID, Title, Author, Category, ISBN, Quantity, AvailableCopies, ShelfLocation FROM Books WHERE Title LIKE ? AND Author LIKE ? AND Category LIKE ?", 
                       (title, author, category))
        rows = cursor.fetchall()
        conn.close()
        self.populate_tree(rows)
        database.log_audit(self.username, "Advanced Search", "Searched for books")
        
    def load_data(self):
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT BookID, Title, Author, Category, ISBN, Quantity, AvailableCopies, ShelfLocation FROM Books")
        rows = cursor.fetchall()
        conn.close()
        self.populate_tree(rows)
        
    def populate_tree(self, rows):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            tag = 'available' if row[6] > 0 else 'unavailable'
            self.tree.insert("", tk.END, values=row, tags=(tag,))
            
    def on_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            row = self.tree.item(selected_item[0])['values']
            self.selected_id = row[0]
            
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT Publisher FROM Books WHERE BookID=?", (self.selected_id,))
            pub = cursor.fetchone()
            conn.close()
            
            self.clear_fields()
            self.txt_title.insert(0, row[1])
            self.txt_author.insert(0, row[2])
            self.cmb_category.set(row[3])
            if pub and pub[0]: self.txt_publisher.insert(0, pub[0])
            if row[4]: self.txt_isbn.insert(0, row[4])
            self.txt_qty.delete(0, tk.END)
            self.txt_qty.insert(0, row[5])
            if len(row) > 7 and row[7]: self.txt_location.insert(0, row[7])
            
    def clear_fields(self):
        self.selected_id = None
        self.txt_title.delete(0, tk.END)
        self.txt_author.delete(0, tk.END)
        self.cmb_category.set('')
        self.txt_publisher.delete(0, tk.END)
        self.txt_isbn.delete(0, tk.END)
        self.txt_qty.delete(0, tk.END)
        self.txt_qty.insert(0, '1')
        self.txt_location.delete(0, tk.END)
