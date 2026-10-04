import tkinter as tk
from tkinter import ttk, messagebox
import database
from datetime import datetime

class MemberManagementFrame(ttk.Frame):
    def __init__(self, parent, username):
        super().__init__(parent)
        self.username = username
        self.create_widgets()
        self.load_data()
        
    def create_widgets(self):
        container = tk.Frame(self, bg="#FFFFFF", highlightbackground="#1E3A5F", highlightthickness=1)
        container.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(container, text="Manage Members", font=('Segoe UI', 14, 'bold'), fg="#1E3A5F", bg="#FFFFFF").grid(row=0, column=0, columnspan=4, pady=(10,5), padx=15, sticky="w")
        
        # Fields
        tk.Label(container, text="Full Name:", bg="#FFFFFF", fg="#172033").grid(row=1, column=0, padx=15, pady=5, sticky="e")
        self.txt_name = ttk.Entry(container, width=35)
        self.txt_name.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(container, text="Email:", bg="#FFFFFF", fg="#172033").grid(row=1, column=2, padx=15, pady=5, sticky="e")
        self.txt_email = ttk.Entry(container, width=35)
        self.txt_email.grid(row=1, column=3, padx=5, pady=5)
        
        tk.Label(container, text="Phone:", bg="#FFFFFF", fg="#172033").grid(row=2, column=0, padx=15, pady=5, sticky="e")
        self.txt_phone = ttk.Entry(container, width=35)
        self.txt_phone.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Label(container, text="Address:", bg="#FFFFFF", fg="#172033").grid(row=2, column=2, padx=15, pady=5, sticky="e")
        self.txt_address = ttk.Entry(container, width=35)
        self.txt_address.grid(row=2, column=3, padx=5, pady=5)
        
        tk.Label(container, text="Membership:", bg="#FFFFFF", fg="#172033").grid(row=3, column=0, padx=15, pady=5, sticky="e")
        self.cmb_type = ttk.Combobox(container, values=["Student", "Teacher", "Public"], width=33)
        self.cmb_type.grid(row=3, column=1, padx=5, pady=5)
        
        # Buttons
        btn_frame = tk.Frame(container, bg="#FFFFFF")
        btn_frame.grid(row=4, column=0, columnspan=4, pady=15)
        
        ttk.Button(btn_frame, text="Add Member", width=15, command=self.add_member).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Update Member", width=15, command=self.update_member).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Deactivate", width=15, command=self.delete_member).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Clear", width=15, style='Secondary.TButton', command=self.clear_fields).pack(side=tk.LEFT, padx=10)
        
        # Search Frame
        search_frame = tk.Frame(self, bg="#F8FAFC")
        search_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(search_frame, text="Search Members:", bg="#F8FAFC", fg="#172033", font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        self.txt_search = ttk.Entry(search_frame, width=40)
        self.txt_search.pack(side=tk.LEFT, padx=10)
        ttk.Button(search_frame, text="Search", command=self.search_members).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="View All", style='Secondary.TButton', command=self.load_data).pack(side=tk.LEFT, padx=5)
        
        # Grid/Treeview
        tree_frame = tk.Frame(self, bg="#FFFFFF")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        columns = ("ID", "Name", "Email", "Phone", "Address", "Type", "Join Date", "Status")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
            
        self.tree.column("ID", width=50)
        self.tree.column("Name", width=150)
        
        self.tree.tag_configure('active', foreground="#1E3A5F")
        self.tree.tag_configure('inactive', foreground="#64748B")
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.selected_id = None
        
    def add_member(self):
        name = self.txt_name.get()
        email = self.txt_email.get()
        phone = self.txt_phone.get()
        addr = self.txt_address.get()
        mtype = self.cmb_type.get()
        join_date = datetime.now().strftime("%Y-%m-%d")
        
        if not name or not phone:
            messagebox.showerror("Error", "Name and Phone are required.")
            return
            
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Members (FullName, Email, Phone, Address, MembershipType, JoinDate) VALUES (?, ?, ?, ?, ?, ?)",
                       (name, email, phone, addr, mtype, join_date))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Member added successfully")
        self.clear_fields()
        self.load_data()
        
    def update_member(self):
        if not self.selected_id:
            messagebox.showerror("Error", "Select a member to update")
            return
            
        name = self.txt_name.get()
        email = self.txt_email.get()
        phone = self.txt_phone.get()
        addr = self.txt_address.get()
        mtype = self.cmb_type.get()
        
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Members SET FullName=?, Email=?, Phone=?, Address=?, MembershipType=? WHERE MemberID=?",
                       (name, email, phone, addr, mtype, self.selected_id))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Member updated successfully")
        self.clear_fields()
        self.load_data()
        
    def delete_member(self):
        if not self.selected_id:
            messagebox.showerror("Error", "Select a member to deactivate")
            return
            
        if messagebox.askyesno("Confirm", "Deactivate this member?"):
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE Members SET Status='Inactive' WHERE MemberID=?", (self.selected_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Member deactivated successfully")
            self.clear_fields()
            self.load_data()
            
    def search_members(self):
        keyword = f"%{self.txt_search.get()}%"
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Members WHERE FullName LIKE ? OR Phone LIKE ? OR Email LIKE ?", (keyword, keyword, keyword))
        rows = cursor.fetchall()
        conn.close()
        self.populate_tree(rows)
        
    def load_data(self):
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Members")
        rows = cursor.fetchall()
        conn.close()
        self.populate_tree(rows)
        
    def populate_tree(self, rows):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            tag = 'active' if row[7] == 'Active' else 'inactive'
            self.tree.insert("", tk.END, values=row, tags=(tag,))
            
    def on_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            row = self.tree.item(selected_item[0])['values']
            self.selected_id = row[0]
            
            self.clear_fields()
            self.txt_name.insert(0, row[1])
            if row[2]: self.txt_email.insert(0, row[2])
            if row[3]: self.txt_phone.insert(0, row[3])
            if row[4]: self.txt_address.insert(0, row[4])
            if row[5]: self.cmb_type.set(row[5])
            
    def clear_fields(self):
        self.selected_id = None
        self.txt_name.delete(0, tk.END)
        self.txt_email.delete(0, tk.END)
        self.txt_phone.delete(0, tk.END)
        self.txt_address.delete(0, tk.END)
        self.cmb_type.set('')
