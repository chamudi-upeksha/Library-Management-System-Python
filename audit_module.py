import tkinter as tk
from tkinter import ttk
import database

class AuditFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        self.load_data()
        
    def create_widgets(self):
        # Header
        header = tk.Frame(self, bg="#FFFFFF", highlightbackground="#1E3A5F", highlightthickness=1)
        header.pack(fill=tk.X, padx=20, pady=20)
        tk.Label(header, text="📝 System Audit Logs", font=('Segoe UI', 14, 'bold'), fg="#1E3A5F", bg="#FFFFFF").pack(anchor="w", padx=15, pady=15)
        
        # Grid/Treeview
        tree_frame = tk.Frame(self, bg="#FFFFFF", highlightbackground="#1E3A5F", highlightthickness=1)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0,20))
        
        columns = ("Log ID", "Username", "Action", "Details", "Date/Time")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
            
        self.tree.column("Details", width=300)
        self.tree.column("Log ID", width=80)
            
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=15)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=15, padx=(0,15))
        
    def load_data(self):
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT LogID, Username, Action, Details, Date FROM AuditLogs ORDER BY LogID DESC LIMIT 100")
        rows = cursor.fetchall()
        conn.close()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert("", tk.END, values=row)
