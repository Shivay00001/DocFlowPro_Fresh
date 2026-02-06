import tkinter as tk
from tkinter import messagebox
from ui.login import LoginView
from ui.dashboard import DashboardView
from auth.manager import AuthManager
from ui.theme import Theme

class DocFlowApp:
    def __init__(self, root):
        self.root = root
        Theme.apply_theme(self.root)
        self.root.title("DocFlow Pro - Enterprise Document Management")
        self.root.geometry("1100x700")

        self.auth_manager = AuthManager()
        self.current_frame = None

        self.show_login()

    def clear_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

    def show_login(self):
        self.clear_frame()
        self.current_frame = LoginView(self.root, self)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def show_dashboard(self):
        if not self.auth_manager.get_current_user():
            messagebox.showwarning("Access Denied", "Please log in first.")
            self.show_login()
            return
            
        self.clear_frame()
        self.current_frame = DashboardView(self.root, self)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def logout(self):
        self.auth_manager.logout()
        self.show_login()
