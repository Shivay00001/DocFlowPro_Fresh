import tkinter as tk
from tkinter import ttk, messagebox
from services.licensing import LicensingService

class SettingsView(tk.Frame):
    def __init__(self, master, app_controller):
        super().__init__(master, bg="#f0f2f5")
        self.app = app_controller
        self.license_service = LicensingService()
        self.pack(fill=tk.BOTH, expand=True)
        
        self.header = tk.Frame(self, bg="#f0f2f5")
        self.header.pack(fill=tk.X, pady=(0, 20))
        tk.Label(self.header, text="Settings", font=("Segoe UI", 20, "bold"), bg="#f0f2f5").pack(side=tk.LEFT)

        self._create_ui()

    def _create_ui(self):
        # Container
        container = tk.Frame(self, bg="white", padx=20, pady=20)
        container.pack(fill=tk.BOTH, expand=True)

        # Profile Section
        tk.Label(container, text="User Profile", font=("Segoe UI", 12, "bold"), bg="white").pack(anchor="w", pady=(0, 10))
        user = self.app.auth_manager.get_current_user()
        tk.Label(container, text=f"Name: {user['full_name']}", bg="white").pack(anchor="w")
        tk.Label(container, text=f"Username: {user['username']}", bg="white").pack(anchor="w")
        tk.Label(container, text=f"Role: {user['role']}", bg="white").pack(anchor="w")

        ttk.Separator(container, orient='horizontal').pack(fill=tk.X, pady=20)

        # License Section
        tk.Label(container, text="License & Plan", font=("Segoe UI", 12, "bold"), bg="white").pack(anchor="w", pady=(0, 10))
        
        self.plan_label = tk.Label(container, text="", font=("Segoe UI", 11), bg="white", fg="#27ae60")
        self.plan_label.pack(anchor="w")
        
        self.update_plan_display()

        tk.Label(container, text="Activate New License:", bg="white").pack(anchor="w", pady=(10, 5))
        self.key_entry = ttk.Entry(container, width=30)
        self.key_entry.pack(anchor="w")
        
        tk.Button(container, text="Activate", bg="#2980b9", fg="white", command=self.activate_license).pack(anchor="w", pady=10)

    def update_plan_display(self):
        plan = self.license_service.get_current_plan()
        text = f"Current Plan: {plan['plan']}"
        if plan['expiry']:
            text += f" (Expires: {plan['expiry']})"
        self.plan_label.config(text=text)

    def activate_license(self):
        key = self.key_entry.get()
        if not key:
            messagebox.showerror("Error", "Please enter a license key.")
            return
            
        success, msg = self.license_service.activate_license(key)
        if success:
            messagebox.showinfo("Success", msg)
            self.update_plan_display()
            self.key_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Activation Failed", msg)
