import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import database
import csv

class ReportFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        
    def create_widgets(self):
        ctrl_frame = tk.Frame(self, bg="#FFFFFF", highlightbackground="#1E3A5F", highlightthickness=1)
        ctrl_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(ctrl_frame, text="Select Report:", bg="#FFFFFF", fg="#172033", font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT, padx=15, pady=15)
        
        self.cmb_report = ttk.Combobox(ctrl_frame, values=[
            "Available Books", 
            "Currently Borrowed Books", 
            "Overdue Books",
            "Fines Collected"
        ], width=35)
        self.cmb_report.pack(side=tk.LEFT, padx=10, pady=15)
        self.cmb_report.current(0)
        
        ttk.Button(ctrl_frame, text="Generate Report", command=self.generate_report).pack(side=tk.LEFT, padx=10, pady=15)
        ttk.Button(ctrl_frame, text="Export CSV", style='Secondary.TButton', command=self.export_csv).pack(side=tk.LEFT, padx=10, pady=15)
        
        tree_frame = tk.Frame(self, bg="#FFFFFF", highlightbackground="#1E3A5F", highlightthickness=1)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        self.tree = ttk.Treeview(tree_frame, show="headings")
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(15,0), pady=15)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=15, padx=(0,15))
        
    def generate_report(self):
        report_type = self.cmb_report.get()
        conn = database.get_connection()
        cursor = conn.cursor()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if report_type == "Available Books":
            columns = ("ID", "Title", "Author", "Category", "Available")
            self.tree.configure(columns=columns)
            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=150)
                
            cursor.execute("SELECT BookID, Title, Author, Category, AvailableCopies FROM Books WHERE AvailableCopies > 0")
            rows = cursor.fetchall()
            
        elif report_type == "Currently Borrowed Books":
            columns = ("Borrow ID", "Member ID", "Book ID", "Borrow Date", "Expected Return")
            self.tree.configure(columns=columns)
            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=150)
                
            cursor.execute("SELECT BorrowID, MemberID, BookID, BorrowDate, ExpectedReturnDate FROM Borrowing WHERE Status='Borrowed'")
            rows = cursor.fetchall()
            
        elif report_type == "Overdue Books":
            columns = ("Borrow ID", "Member ID", "Book ID", "Expected Return")
            self.tree.configure(columns=columns)
            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=150)
                
            cursor.execute("SELECT BorrowID, MemberID, BookID, ExpectedReturnDate FROM Borrowing WHERE Status='Borrowed' AND ExpectedReturnDate < date('now')")
            rows = cursor.fetchall()
            
        elif report_type == "Fines Collected":
            columns = ("Fine ID", "Borrow ID", "Member ID", "Amount", "Date", "Status")
            self.tree.configure(columns=columns)
            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=120)
                
            cursor.execute("SELECT * FROM Fines")
            rows = cursor.fetchall()
            
        for row in rows:
            self.tree.insert("", tk.END, values=row)
            
        conn.close()
        
    def export_csv(self):
        if not self.tree.get_children():
            messagebox.showwarning("Warning", "No data to export.")
            return
            
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                headers = [self.tree.heading(col)['text'] for col in self.tree['columns']]
                writer.writerow(headers)
                for item in self.tree.get_children():
                    writer.writerow(self.tree.item(item)['values'])
            messagebox.showinfo("Success", f"Report exported to {file_path}")
