import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
from datetime import datetime
import sys
import os

try:
    from PIL import Image, ImageTk
except ImportError:
    pass

sys.path.append(r"D:\LibraryManagementSystem")
import database

COLORS = {
    "primary": "#1E3A5F",
    "secondary": "#2A9D8F",
    "accent": "#E9C46A",
    "bg": "#ECF0F5",
    "card_bg": "#FFFFFF",
    "main_text": "#172033",
    "sec_text": "#64748B",
    "success": "#22C55E",
    "warning": "#F59E0B",
    "error": "#EF4444",
    "sidebar_bg": "#222D32",
    "sidebar_hover": "#1E282C",
    "sidebar_text": "#B8C7CE",
    "sidebar_active": "#2A9D8F"
}

def setup_modern_styles():
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('.', background=COLORS["bg"], foreground=COLORS["main_text"], font=('Segoe UI', 10))
    style.configure('TFrame', background=COLORS["bg"])
    style.configure('TEntry', fieldbackground=COLORS["card_bg"], padding=5)
    style.configure('TCombobox', fieldbackground=COLORS["card_bg"], padding=5)
    style.configure('Treeview', background=COLORS["card_bg"], fieldbackground=COLORS["card_bg"], foreground=COLORS["main_text"], rowheight=30, borderwidth=0)
    style.configure('Treeview.Heading', background=COLORS["primary"], foreground="#FFFFFF", font=('Segoe UI', 10, 'bold'), padding=5)
    style.map('Treeview.Heading', background=[('active', COLORS["secondary"])])
    style.map('Treeview', background=[('selected', COLORS["secondary"])], foreground=[('selected', "#FFFFFF")])

class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Library Management System - Login")
        self.geometry("750x450")
        self.configure(bg=COLORS["card_bg"])
        self.resizable(False, False)
        self.eval('tk::PlaceWindow . center')
        
        setup_modern_styles()
        database.setup_database()
        
        self.left_frame = tk.Frame(self, bg=COLORS["primary"], width=350, height=450)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.left_frame.pack_propagate(False)
        
        try:
            img_path = r"C:\Users\Laptop Outlet\.gemini\antigravity\brain\89e9cd61-99e1-46b0-ac39-b547ac9d2f96\.user_uploaded\media_1790557031661.jpg"
            img = Image.open(img_path)
            img = img.resize((350, 450), Image.Resampling.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(img)
            lbl_img = tk.Label(self.left_frame, image=self.bg_image, borderwidth=0)
            lbl_img.pack(fill=tk.BOTH, expand=True)
        except Exception:
            tk.Label(self.left_frame, text="Library\nManagement", font=('Segoe UI', 24, 'bold'), fg="#FFFFFF", bg=COLORS["primary"], justify="center").pack(expand=True)
        
        self.right_frame = tk.Frame(self, bg=COLORS["card_bg"], width=400, height=450)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        form_frame = tk.Frame(self.right_frame, bg=COLORS["card_bg"])
        form_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(form_frame, text="Welcome Back", font=('Segoe UI', 22, 'bold'), fg=COLORS["primary"], bg=COLORS["card_bg"]).pack(pady=(0, 5))
        tk.Label(form_frame, text="Sign in to your account", font=('Segoe UI', 10), fg=COLORS["sec_text"], bg=COLORS["card_bg"]).pack(pady=(0, 30))
        
        tk.Label(form_frame, text="Username", font=('Segoe UI', 9, 'bold'), fg=COLORS["main_text"], bg=COLORS["card_bg"]).pack(anchor="w")
        self.txt_username = ttk.Entry(form_frame, width=35, font=('Segoe UI', 11))
        self.txt_username.pack(pady=(5, 15), ipady=3)
        
        tk.Label(form_frame, text="Password", font=('Segoe UI', 9, 'bold'), fg=COLORS["main_text"], bg=COLORS["card_bg"]).pack(anchor="w")
        self.txt_password = ttk.Entry(form_frame, show="*", width=35, font=('Segoe UI', 11))
        self.txt_password.pack(pady=(5, 25), ipady=3)
        
        btn_login = tk.Button(form_frame, text="LOGIN", font=('Segoe UI', 10, 'bold'), bg=COLORS["primary"], fg="#FFFFFF", 
                              relief=tk.FLAT, activebackground=COLORS["secondary"], activeforeground="#FFFFFF",
                              cursor="hand2", command=self.login)
        btn_login.pack(fill=tk.X, ipady=8)
        self.bind('<Return>', lambda event: self.login())
        
    def login(self):
        username = self.txt_username.get().strip()
        password = self.txt_password.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return
            
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT UserID, Role FROM Users WHERE Username = ? AND Password = ?", (username, hashed_pw))
        user = cursor.fetchone()
        
        if user:
            cursor.execute("UPDATE Users SET LastLogin = ? WHERE UserID = ?", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user[0]))
            conn.commit()
            conn.close()
            database.log_audit(username, "Login", "User successfully logged in")
            self.destroy()
            app = MainDashboard(user[1], username)
            app.mainloop()
        else:
            conn.close()
            messagebox.showerror("Error", "Invalid username or password.")


class MainDashboard(tk.Tk):
    def __init__(self, role, username):
        super().__init__()
        self.title("Library Management System")
        self.geometry("1200x750")
        self.configure(bg=COLORS["bg"])
        self.state('zoomed')
        
        self.role = role
        self.username = username
        self.current_frame = None
        
        setup_modern_styles()
        self.create_layout()
        
    def create_layout(self):
        # HEADER
        self.header = tk.Frame(self, bg=COLORS["accent"], height=60)
        self.header.pack(side=tk.TOP, fill=tk.X)
        self.header.pack_propagate(False)
        
        title_frame = tk.Frame(self.header, bg="#D4A72C", width=230, height=60)
        title_frame.pack(side=tk.LEFT, fill=tk.Y)
        title_frame.pack_propagate(False)
        tk.Label(title_frame, text="Library System", font=('Segoe UI', 14, 'bold'), fg="#FFFFFF", bg="#D4A72C").pack(expand=True)
        
        tk.Button(self.header, text="Logout", font=('Segoe UI', 9, 'bold'), bg="#FFFFFF", fg=COLORS["main_text"], 
                  relief=tk.FLAT, cursor="hand2", padx=15, command=self.destroy).pack(side=tk.RIGHT, padx=20, pady=15)
        tk.Label(self.header, text=f"Welcome, {self.username.capitalize()} ({self.role})", font=('Segoe UI', 11), fg="#FFFFFF", bg=COLORS["accent"]).pack(side=tk.RIGHT, padx=10)
        
        self.main_container = tk.Frame(self, bg=COLORS["bg"])
        self.main_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # SIDEBAR
        self.sidebar = tk.Frame(self.main_container, bg=COLORS["sidebar_bg"], width=230)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        
        user_info = tk.Frame(self.sidebar, bg=COLORS["sidebar_bg"])
        user_info.pack(fill=tk.X, pady=20, padx=15)
        
        canvas = tk.Canvas(user_info, width=40, height=40, bg=COLORS["sidebar_bg"], highlightthickness=0)
        canvas.grid(row=0, column=0, rowspan=2, padx=(0, 10))
        canvas.create_oval(2, 2, 38, 38, fill=COLORS["accent"], outline="")
        canvas.create_text(20, 20, text=self.username[0].upper(), fill="#FFFFFF", font=('Segoe UI', 14, 'bold'))
        
        tk.Label(user_info, text=self.username, font=('Segoe UI', 11, 'bold'), fg="#FFFFFF", bg=COLORS["sidebar_bg"]).grid(row=0, column=1, sticky="w")
        tk.Label(user_info, text="● Online", font=('Segoe UI', 8), fg=COLORS["success"], bg=COLORS["sidebar_bg"]).grid(row=1, column=1, sticky="w")
        
        tk.Label(self.sidebar, text="MAIN NAVIGATION", font=('Segoe UI', 8, 'bold'), fg=COLORS["sidebar_text"], bg="#1A2226", anchor="w", padx=15, pady=10).pack(fill=tk.X)
        
        self.nav_buttons = []
        self.create_nav_item("📊 Dashboard", self.show_dashboard)
        self.create_nav_item("📚 Books Management", self.show_books)
        self.create_nav_item("👥 Members Management", self.show_members)
        self.create_nav_item("🔄 Borrow / Return", self.show_borrow)
        self.create_nav_item("📅 Reservations", self.show_reservations)
        self.create_nav_item("📈 Reports / Export", self.show_reports)
        if self.role == "Admin":
            self.create_nav_item("📝 Audit Logs", self.show_audit)
        
        self.content_area = tk.Frame(self.main_container, bg=COLORS["bg"])
        self.content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.show_dashboard(self.nav_buttons[0])
        
    def create_nav_item(self, text, command):
        btn = tk.Button(self.sidebar, text=f"  {text}", font=('Segoe UI', 10), fg=COLORS["sidebar_text"], bg=COLORS["sidebar_bg"],
                        anchor="w", relief=tk.FLAT, cursor="hand2", pady=10, padx=15, command=lambda: command(btn))
        btn.pack(fill=tk.X)
        btn.bind("<Enter>", lambda e, b=btn: self.on_nav_enter(b))
        btn.bind("<Leave>", lambda e, b=btn: self.on_nav_leave(b))
        self.nav_buttons.append(btn)
        
    def on_nav_enter(self, btn):
        if getattr(btn, 'is_active', False) != True:
            btn.config(bg=COLORS["sidebar_hover"], fg="#FFFFFF")
            
    def on_nav_leave(self, btn):
        if getattr(btn, 'is_active', False) != True:
            btn.config(bg=COLORS["sidebar_bg"], fg=COLORS["sidebar_text"])
            
    def set_active_nav(self, active_btn):
        for btn in self.nav_buttons:
            btn.config(bg=COLORS["sidebar_bg"], fg=COLORS["sidebar_text"])
            btn.is_active = False
        active_btn.config(bg=COLORS["sidebar_hover"], fg="#FFFFFF")
        active_btn.is_active = True
        
    def clear_content(self):
        if self.current_frame is not None:
            self.current_frame.destroy()
            
    def show_dashboard(self, btn=None):
        if btn: self.set_active_nav(btn)
        self.clear_content()
        
        self.current_frame = tk.Frame(self.content_area, bg=COLORS["bg"])
        self.current_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        header_frame = tk.Frame(self.current_frame, bg=COLORS["bg"])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        tk.Label(header_frame, text="System Dashboard", font=('Segoe UI', 18, 'bold'), fg=COLORS["main_text"], bg=COLORS["bg"]).pack(side=tk.LEFT)
        tk.Label(header_frame, text="Real-time analytics", font=('Segoe UI', 10), fg=COLORS["sec_text"], bg=COLORS["bg"]).pack(side=tk.LEFT, padx=10, pady=(8,0))
        
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Books")
        total_books = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Members")
        total_members = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Borrowing WHERE Status='Borrowed'")
        borrowed_books = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Borrowing WHERE Status='Borrowed' AND ExpectedReturnDate < date('now')")
        overdue_books = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Reservations WHERE Status='Pending'")
        pending_reservations = cursor.fetchone()[0]
        conn.close()
        
        # TOP COLORED CARDS
        grid_frame = tk.Frame(self.current_frame, bg=COLORS["bg"])
        grid_frame.pack(fill=tk.X)
        grid_frame.columnconfigure((0,1,2,3), weight=1)
        
        self.create_color_card(grid_frame, "Total Books", total_books, COLORS["secondary"], 0, lambda: self.show_books(self.nav_buttons[1]))
        self.create_color_card(grid_frame, "Members", total_members, COLORS["success"], 1, lambda: self.show_members(self.nav_buttons[2]))
        self.create_color_card(grid_frame, "Borrowed", borrowed_books, COLORS["warning"], 2, lambda: self.show_borrow(self.nav_buttons[3]))
        self.create_color_card(grid_frame, "Overdue", overdue_books, COLORS["error"], 3, lambda: self.show_reports(self.nav_buttons[5]))
        
        # MIDDLE SECTION: White Cards + Recent Activity Treeview
        middle_grid = tk.Frame(self.current_frame, bg=COLORS["bg"])
        middle_grid.pack(fill=tk.BOTH, expand=True, pady=20)
        
        left_middle = tk.Frame(middle_grid, bg=COLORS["bg"], width=300)
        left_middle.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_middle.pack_propagate(False)
        
        self.create_white_card(left_middle, "PENDING HOLDS", pending_reservations, COLORS["primary"]).pack(fill=tk.X, pady=(0, 10))
        self.create_white_card(left_middle, "SYSTEM STATUS", "ONLINE", COLORS["success"]).pack(fill=tk.X)
        
        right_middle = tk.Frame(middle_grid, bg="#FFFFFF", highlightbackground="#1E3A5F", highlightthickness=1)
        right_middle.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(right_middle, text="🕒 Recent Borrowings", font=('Segoe UI', 11, 'bold'), fg="#1E3A5F", bg="#FFFFFF").pack(anchor="w", padx=15, pady=10)
        
        tree_frame = tk.Frame(right_middle, bg="#FFFFFF")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        columns = ("ID", "Member", "Book", "Date", "Status")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
        tree.column("ID", width=50)
        tree.column("Member", width=80)
        tree.column("Book", width=120)
        tree.column("Date", width=100)
        tree.column("Status", width=80)
        
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT BorrowID, MemberID, BookID, BorrowDate, Status FROM Borrowing ORDER BY BorrowID DESC LIMIT 8")
        recent = cursor.fetchall()
        conn.close()
        for r in recent:
            tree.insert("", tk.END, values=r)
            
        tree.pack(fill=tk.BOTH, expand=True)
        
    def create_color_card(self, parent, title, value, color, col, command=None):
        card = tk.Frame(parent, bg=color, height=145)
        card.grid(row=0, column=col, padx=10, pady=10, sticky="nsew")
        card.pack_propagate(False)
        tk.Label(card, text=str(value), font=('Segoe UI', 32, 'bold'), fg="#FFFFFF", bg=color).pack(anchor="w", padx=15, pady=(10, 0))
        tk.Label(card, text=title, font=('Segoe UI', 12), fg="#FFFFFF", bg=color).pack(anchor="w", padx=15)
        
        strip = tk.Frame(card, bg=self.adjust_color_darker(color), height=30, cursor="hand2" if command else "")
        strip.place(relx=0, rely=1.0, anchor="sw", relwidth=1.0)
        lbl = tk.Label(strip, text="More info ➜", font=('Segoe UI', 9), fg="#FFFFFF", bg=self.adjust_color_darker(color), cursor="hand2" if command else "")
        lbl.pack(pady=5)
        
        if command:
            strip.bind("<Button-1>", lambda e: command())
            lbl.bind("<Button-1>", lambda e: command())
        
    def create_white_card(self, parent, title, value, color):
        card = tk.Frame(parent, bg=COLORS["card_bg"], height=80)
        card.pack_propagate(False)
        left_block = tk.Frame(card, bg=color, width=80)
        left_block.pack(side=tk.LEFT, fill=tk.Y)
        left_block.pack_propagate(False)
        tk.Label(card, text=title, font=('Segoe UI', 10), fg=COLORS["sec_text"], bg=COLORS["card_bg"]).pack(anchor="w", padx=15, pady=(15, 0))
        tk.Label(card, text=str(value), font=('Segoe UI', 16, 'bold'), fg=COLORS["main_text"], bg=COLORS["card_bg"]).pack(anchor="w", padx=15)
        return card

    def adjust_color_darker(self, hex_color):
        if hex_color == COLORS["secondary"]: return "#1F7A6F"
        if hex_color == COLORS["success"]: return "#1B9C4B"
        if hex_color == COLORS["warning"]: return "#C27A05"
        if hex_color == COLORS["error"]: return "#B32F2F"
        return "#000000"

    def show_books(self, btn=None):
        if btn: self.set_active_nav(btn)
        self.clear_content()
        import book_module
        self.current_frame = book_module.BookManagementFrame(self.content_area, self.username)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def show_members(self, btn=None):
        if btn: self.set_active_nav(btn)
        self.clear_content()
        import member_module
        self.current_frame = member_module.MemberManagementFrame(self.content_area, self.username)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def show_borrow(self, btn=None):
        if btn: self.set_active_nav(btn)
        self.clear_content()
        import borrow_module
        self.current_frame = borrow_module.BorrowReturnFrame(self.content_area, self.username)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def show_reservations(self, btn=None):
        if btn: self.set_active_nav(btn)
        self.clear_content()
        import reservation_module
        self.current_frame = reservation_module.ReservationFrame(self.content_area, self.username)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def show_reports(self, btn=None):
        if btn: self.set_active_nav(btn)
        self.clear_content()
        import report_module
        self.current_frame = report_module.ReportFrame(self.content_area)
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        
    def show_audit(self, btn=None):
        if btn: self.set_active_nav(btn)
        self.clear_content()
        import audit_module
        self.current_frame = audit_module.AuditFrame(self.content_area)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()
