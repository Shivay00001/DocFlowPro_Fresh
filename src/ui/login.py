from ui.theme import Theme
import tkinter as tk
from tkinter import ttk, messagebox

class LoginView(tk.Frame):
    def __init__(self, master, app_controller):
        super().__init__(master, bg=Theme.BG_MAIN)
        self.app = app_controller
        self.pack(fill=tk.BOTH, expand=True)
        
        self._create_widgets()

    def _create_widgets(self):
        # Center Container
        container = tk.Frame(self, bg=Theme.BG_MAIN)
        container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Card
        center_frame = Theme.create_card_frame(container, padding=50)
        center_frame.pack(fill=tk.BOTH)

        # Title
        tk.Label(center_frame, text="DocFlow Pro", font=Theme.FONT_HEADER, bg=Theme.BG_WHITE, fg=Theme.PRIMARY).pack(pady=(0, 10))
        tk.Label(center_frame, text="Secure Enterprise Login", font=Theme.FONT_SMALL, bg=Theme.BG_WHITE, fg=Theme.TEXT_LIGHT).pack(pady=(0, 40))

        # Username
        tk.Label(center_frame, text="Username", font=("Segoe UI", 10, "bold"), bg=Theme.BG_WHITE, anchor="w").pack(fill=tk.X)
        self.username_entry = ttk.Entry(center_frame, font=Theme.FONT_BODY)
        self.username_entry.pack(fill=tk.X, pady=(5, 20))

        # Password
        tk.Label(center_frame, text="Password", font=("Segoe UI", 10, "bold"), bg=Theme.BG_WHITE, anchor="w").pack(fill=tk.X)
        self.password_entry = ttk.Entry(center_frame, font=Theme.FONT_BODY, show="*")
        self.password_entry.pack(fill=tk.X, pady=(5, 30))

        # Buttons
        login_btn = tk.Button(center_frame, text="LOGIN", font=("Segoe UI", 11, "bold"), 
                             bg=Theme.PRIMARY, fg="white", relief=tk.FLAT, pady=8,
                             cursor="hand2", command=self.handle_login)
        login_btn.pack(fill=tk.X)

        tk.Button(center_frame, text="Create New Account", font=Theme.FONT_SMALL,
                 bg=Theme.BG_WHITE, fg=Theme.TEXT_LIGHT, relief=tk.FLAT, 
                 cursor="hand2", command=self.handle_register).pack(pady=(15, 0))

    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password")
            return

        success, message = self.app.auth_manager.login(username, password)
        if success:
            self.app.show_dashboard()
        else:
            messagebox.showerror("Login Failed", message)

    def handle_register(self):
        # Quick toggle to a register popup or mode
        RegisterDialog(self)

class RegisterDialog(tk.Toplevel):
    def __init__(self, parent_view):
        super().__init__(parent_view)
        self.title("Register New User")
        self.geometry("400x450")
        self.parent = parent_view
        
        self._create_widgets()
        
    def _create_widgets(self):
        main_frame = tk.Frame(self, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        fields = ["Full Name", "Username", "Email", "Password"]
        self.entries = {}
        
        tk.Label(main_frame, text="Create Account", font=("Segoe UI", 16, "bold")).pack(pady=(0, 20))

        for field in fields:
            tk.Label(main_frame, text=field, anchor="w").pack(fill=tk.X)
            entry = ttk.Entry(main_frame)
            if field == "Password":
                entry.configure(show="*")
            entry.pack(fill=tk.X, pady=(5, 10))
            self.entries[field] = entry
            
        tk.Button(main_frame, text="Register", bg="#34a853", fg="white", 
                 command=self.submit_registration).pack(fill=tk.X, pady=20)

    def submit_registration(self):
        full_name = self.entries["Full Name"].get()
        username = self.entries["Username"].get()
        email = self.entries["Email"].get()
        password = self.entries["Password"].get()
        
        if not all([full_name, username, password]):
            messagebox.showerror("Error", "Full Name, Username, and Password are required.")
            return

        success, message = self.parent.app.auth_manager.register_user(full_name, username, password, email)
        
        if success:
            messagebox.showinfo("Success", "Registration successful! Please login.")
            self.destroy()
        else:
            messagebox.showerror("Error", message)
