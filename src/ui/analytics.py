import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from services.analytics import AnalyticsService

class AnalyticsView(tk.Frame):
    def __init__(self, master, app_controller):
        super().__init__(master, bg="#f0f2f5")
        self.app = app_controller
        self.service = AnalyticsService()
        self.pack(fill=tk.BOTH, expand=True)
        
        self.header = tk.Frame(self, bg="#f0f2f5")
        self.header.pack(fill=tk.X, pady=(0, 20))
        tk.Label(self.header, text="Business Intelligence", font=("Segoe UI", 20, "bold"), bg="#f0f2f5").pack(side=tk.LEFT)

        self._create_chart()

    def _create_chart(self):
        # Data
        data = self.service.get_monthly_revenue(self.app.auth_manager.get_current_user()['id'])
        
        if not data:
            tk.Label(self, text="No sufficient data to generate charts.", font=("Segoe UI", 12), bg="#f0f2f5").pack(pady=50)
            return

        months = [row[0] for row in data]
        amounts = [row[1] for row in data]

        # Figure
        fig = Figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111)
        
        ax.bar(months, amounts, color='#3498db')
        ax.set_title("Monthly Revenue Trend")
        ax.set_xlabel("Month")
        ax.set_ylabel("Revenue (INR)")
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        # Canvas
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
