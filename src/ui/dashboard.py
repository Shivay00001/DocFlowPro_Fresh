import tkinter as tk
from tkinter import ttk, messagebox

class DashboardView(tk.Frame):
    def __init__(self, master, app_controller):
        super().__init__(master, bg="#f0f2f5")
        self.app = app_controller
        self.user = self.app.auth_manager.get_current_user()
        
        self.pack(fill=tk.BOTH, expand=True)
        self._create_layout()

    def _create_layout(self):
        # Header
        self.header = tk.Frame(self, bg="#ffffff", height=60, relief=tk.RAISED, bd=1)
        self.header.pack(side=tk.TOP, fill=tk.X)
        self.header.pack_propagate(False)

        tk.Label(self.header, text="DocFlow Pro", font=("Segoe UI", 18, "bold"), fg="#1a73e8", bg="white").pack(side=tk.LEFT, padx=20)
        
        user_info = f"Welcome, {self.user['full_name']} ({self.user['role']})"
        tk.Label(self.header, text=user_info, font=("Segoe UI", 10), bg="white").pack(side=tk.RIGHT, padx=10)
        
        tk.Button(self.header, text="Logout", bg="#ea4335", fg="white", relief=tk.FLAT,
                 command=self.app.logout).pack(side=tk.RIGHT, padx=20)

        # Main Container
        self.main_container = tk.Frame(self, bg="#f0f2f5")
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        self.sidebar = tk.Frame(self.main_container, bg="#2c3e50", width=250)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # Content Area
        self.content_area = tk.Frame(self.main_container, bg="#f0f2f5", padx=20, pady=20)
        self.content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_sidebar_menu()
        self.show_home() # Default View

    def _build_sidebar_menu(self):
        buttons = [
            ("Dashboard", self.show_home),
            ("Upload Documents", self.show_upload),
            ("Invoices", self.show_invoices),
            ("Workflows", self.show_workflows),
            ("Analytics (Premium)", self.show_analytics),
            ("Settings", self.show_settings)
        ]

        for text, command in buttons:
            btn = tk.Button(self.sidebar, text=text, font=("Segoe UI", 11), 
                           bg="#34495e", fg="white", activebackground="#2980b9", activeforeground="white",
                           relief=tk.FLAT, anchor="w", padx=20, command=command)
            btn.pack(fill=tk.X, pady=1)

    def _clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def show_home(self):
        self._clear_content()
        tk.Label(self.content_area, text="Dashboard Overview", font=("Segoe UI", 20), bg="#f0f2f5").pack(anchor="w")
        
        # Real Stats
        from services.analytics import AnalyticsService
        stats = AnalyticsService().get_dashboard_stats(self.user['id'])
        
        # Stats Cards
        grid = tk.Frame(self.content_area, bg="#f0f2f5")
        grid.pack(fill=tk.X, pady=20)
        
        self._create_stat_card(grid, "Pending Docs", str(stats.get('pending_docs', 0)), "#f1c40f", 0)
        self._create_stat_card(grid, "Processed", str(stats.get('processed_docs', 0)), "#2ecc71", 1)
        self._create_stat_card(grid, "Rejected", str(stats.get('rejected_docs', 0)), "#e74c3c", 2)
        revenue = stats.get('total_revenue', 0)
        self._create_stat_card(grid, "Total Revenue", f"₹{revenue:,.2f}", "#3498db", 3)


    def _create_stat_card(self, parent, title, value, color, col_idx):
        card = tk.Frame(parent, bg="white", width=200, height=100, padx=20, pady=20, relief=tk.RAISED, bd=1)
        card.grid(row=0, column=col_idx, padx=10, sticky="nsew")
        
        tk.Label(card, text=title, font=("Segoe UI", 10), bg="white", fg="#7f8c8d").pack(anchor="w")
        tk.Label(card, text=value, font=("Segoe UI", 18, "bold"), bg="white", fg=color).pack(anchor="w")

    def show_upload(self):
        self._clear_content()
        tk.Label(self.content_area, text="Upload Documents", font=("Segoe UI", 20), bg="#f0f2f5").pack(anchor="w")
        
        # Dashed Border Box Simulation using Canvas
        upload_area = tk.Canvas(self.content_area, bg="white", height=300, bd=0, highlightthickness=0)
        upload_area.pack(fill=tk.X, pady=40, padx=20)
        
        # Draw dashed border
        upload_area.update()
        w, h = upload_area.winfo_width(), 300
        # Wait for update might be flickery, setting default width
        w = 900 
        
        # Visuals inside canvas
        # Since canvas is tricky for widgets without coordinates, we'll use a frame inside it or just a frame with groove relief
        
        # Simpler approach: Frame with custom relief or just visual styling
        upload_frame = tk.Frame(self.content_area, bg="white", padx=40, pady=60, relief=tk.GROOVE, bd=2)
        upload_frame.pack(fill=tk.BOTH, expand=True, pady=20, padx=20)
        
        tk.Label(upload_frame, text="📂", font=("Segoe UI", 48), bg="white", fg="#3498db").pack()
        tk.Label(upload_frame, text="Drag & Drop your invoices here", font=("Segoe UI", 16), bg="white", fg="#2c3e50").pack(pady=(10, 5))
        tk.Label(upload_frame, text="Supports PDF, JPG, PNG", font=("Segoe UI", 10), bg="white", fg="gray").pack(pady=(0, 20))
        
        tk.Button(upload_frame, text="Select Files from Computer", font=("Segoe UI", 12, "bold"), 
                 bg="#3498db", fg="white", relief=tk.FLAT, padx=20, pady=10, cursor="hand2",
                 command=self.handle_file_select).pack()
        
        self.status_label = tk.Label(upload_frame, text="", bg="white", fg="gray")
        self.status_label.pack(pady=10)

    def handle_file_select(self):
        from tkinter import filedialog
        from services.document import DocumentService
        
        filenames = filedialog.askopenfilenames(
            title="Select Documents",
            filetypes=[("Documents", "*.pdf *.png *.jpg *.jpeg")]
        )
        
        if not filenames:
            return
            
        doc_service = DocumentService()
        uploaded_count = 0
        
        for f in filenames:
            success, result = doc_service.upload_document(self.user['id'], f)
            if success:
                uploaded_count += 1
                # Trigger processing
                proc_success, proc_data = doc_service.process_document(result)
                if not proc_success:
                    messagebox.showerror("Processing Failed", f"Uploaded but failed to process {os.path.basename(f)}.\nError: {proc_data}")
            else:
                messagebox.showerror("Upload Error", f"Failed to upload {os.path.basename(f)}: {result}")
        
        self.status_label.config(text=f"Uploaded {uploaded_count} documents.")


    def show_invoices(self):
        self._clear_content()
        from ui.invoices import InvoicesView
        InvoicesView(self.content_area, self.app)

    def show_workflows(self):
        self._clear_content()
        from ui.workflows import WorkflowView
        WorkflowView(self.content_area, self.app)

    def show_analytics(self):
        self._clear_content()
        
        # Feature Gating
        from services.licensing import LicensingService
        if not LicensingService().can_access("analytics"):
            tk.Label(self.content_area, text="Analytics is a Premium Feature", font=("Segoe UI", 20), bg="#f0f2f5", fg="#7f8c8d").pack(pady=50)
            tk.Label(self.content_area, text="Please upgrade to Pro to view insights.", font=("Segoe UI", 12), bg="#f0f2f5").pack()
            tk.Button(self.content_area, text="Go to Settings", command=self.show_settings, bg="#3498db", fg="white").pack(pady=20)
            return

        from ui.analytics import AnalyticsView
        AnalyticsView(self.content_area, self.app)

        
    def show_settings(self):
        self._clear_content()
        from ui.settings import SettingsView
        SettingsView(self.content_area, self.app)
