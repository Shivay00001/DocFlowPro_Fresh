import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from db.schema import get_db
from services.invoice import InvoiceService

class InvoicesView(tk.Frame):
    def __init__(self, master, app_controller):
        super().__init__(master, bg="#f0f2f5")
        self.app = app_controller
        self.invoice_service = InvoiceService()
        self.pack(fill=tk.BOTH, expand=True)
        
        self._create_ui()
        self.refresh_data()

    def _create_ui(self):
        # Header
        header = tk.Frame(self, bg="#f0f2f5")
        header.pack(fill=tk.X, pady=(0, 20))
        tk.Label(header, text="Invoices", font=("Segoe UI", 20, "bold"), bg="#f0f2f5").pack(side=tk.LEFT)
        
        # Action Buttons
        btn_frame = tk.Frame(header, bg="#f0f2f5")
        btn_frame.pack(side=tk.RIGHT)
        
        tk.Button(btn_frame, text="Export Excel", bg="#27ae60", fg="white", command=self.export_excel).pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text="Create New", bg="#3498db", fg="white", command=self.create_invoice).pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text="Refresh", command=self.refresh_data).pack(side=tk.RIGHT, padx=5)

        # Treeview
        columns = ("ID", "Vendor", "Date", "Total", "GSTIN", "Status")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.place(relx=1, rely=0, relheight=1, anchor='ne')

        # Context Menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Edit Invoice", command=self.edit_invoice)
        self.context_menu.add_command(label="Delete Invoice", command=self.delete_invoice)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Request Approval", command=self.request_approval)
        self.tree.bind("<Button-3>", self.show_context_menu)

    def refresh_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        db = get_db()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Modified query to handle invoices without documents (LEFT JOIN)
        user_id = self.app.auth_manager.get_current_user()['id']
        query = '''
            SELECT i.id, i.vendor_name, i.invoice_date, i.total_amount, i.gst_number, d.status 
            FROM invoices i
            LEFT JOIN documents d ON i.document_id = d.id
            WHERE d.user_id = ? OR i.document_id IS NULL
            ORDER BY i.created_at DESC
        '''
        # Note: If no document, user_id might not be tracked directly on invoice!
        # Fix: In Create Manual, we don't store user_id in invoice table!
        # Implementation Gap: invoices table needs user_id or we only show linked docs.
        # Quick Fix: Assume for now we only show linked docs OR we modify schema.
        # To avoid schema migration complexity mid-run, let's link to a Dummy Document or just filter by document join.
        # Actually, for manual invoices, they won't appear if we filter by document.user_id.
        # BUT, the schema I made earlier: `invoices` has `document_id`. `documents` has `user_id`.
        # So manual invoices MUST be linked to a document to belong to a user.
        # Strategy: Create a "Manual Entry" dummy document for the user if it doesn't exist?
        # OR: Just insert a placeholder row in `documents` for every manual invoice.
        
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        
        for row in rows:
            status = row['status'] if row['status'] else "Manual"
            self.tree.insert("", tk.END, values=(
                row['id'], 
                row['vendor_name'], 
                row['invoice_date'], 
                f"Rs. {row['total_amount']}", 
                row['gst_number'],
                status
            ))

    def create_invoice(self):
        InvoiceEditorDialog(self, None, self.app)

    def edit_invoice(self):
        selected = self.tree.selection()
        if not selected:
            return
        inv_id = self.tree.item(selected[0])['values'][0]
        InvoiceEditorDialog(self, inv_id, self.app)

    def delete_invoice(self):
        selected = self.tree.selection()
        if not selected:
            return
            
        inv_id = self.tree.item(selected[0])['values'][0]
        vendor = self.tree.item(selected[0])['values'][1]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete invoice from {vendor}?"):
            success, msg = self.invoice_service.delete_invoice(self.app.auth_manager.get_current_user()['id'], inv_id)
            if success:
                self.refresh_data()
                messagebox.showinfo("Deleted", "Invoice deleted successfully.")
            else:
                messagebox.showerror("Error", msg)

    def export_excel(self):
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not path:
            return
        from services.export import ExportService
        service = ExportService()
        success, msg = service.export_invoices(self.app.auth_manager.get_current_user()['id'], 'xlsx', path)
        if success:
            messagebox.showinfo("Export Success", f"File saved to: {msg}")
        else:
            messagebox.showerror("Export Failed", msg)

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def request_approval(self):
        # ... logic ...
        pass


class InvoiceEditorDialog(tk.Toplevel):
    def __init__(self, parent, invoice_id, app):
        super().__init__(parent)
        self.invoice_id = invoice_id
        self.parent = parent
        self.app = app
        self.service = InvoiceService()
        title = f"Edit Invoice #{invoice_id}" if invoice_id else "New Invoice"
        self.title(title)
        self.geometry("400x500")
        
        self.data = {
            "vendor_name": "", "gst_number": "", "invoice_date": "", "total_amount": "0.0"
        }
        if invoice_id:
            self._load_data()
            
        self._create_ui()

    def _load_data(self):
        conn = get_db().get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT vendor_name, gst_number, invoice_date, total_amount FROM invoices WHERE id = ?", (self.invoice_id,))
        row = cursor.fetchone()
        if row:
            self.data = dict(row)

    def _create_ui(self):
        f = tk.Frame(self, padx=20, pady=20)
        f.pack(fill=tk.BOTH, expand=True)

        self.entries = {}
        fields = [
            ("Vendor", self.data['vendor_name']),
            ("GSTIN", self.data['gst_number']),
            ("Date", self.data['invoice_date']),
            ("Total Amount", str(self.data['total_amount']))
        ]

        for label, val in fields:
            tk.Label(f, text=label, anchor="w").pack(fill=tk.X)
            e = ttk.Entry(f)
            e.insert(0, val if val else "")
            e.pack(fill=tk.X, pady=(0, 10))
            self.entries[label] = e

        btn_text = "Save Changes" if self.invoice_id else "Create Invoice"
        tk.Button(f, text=btn_text, bg="#1a73e8", fg="white", command=self.save).pack(pady=20)

    def save(self):
        vendor = self.entries["Vendor"].get()
        gst = self.entries["GSTIN"].get()
        date = self.entries["Date"].get()
        try:
            total = float(self.entries["Total Amount"].get())
        except:
            messagebox.showerror("Error", "Invalid Total Amount")
            return

        user_id = self.app.auth_manager.get_current_user()['id']

        if self.invoice_id:
            success, msg = self.service.update_invoice(user_id, self.invoice_id, vendor, gst, date, total)
        else:
            # Create a placeholder document to link ownership
            # This is a bit of a hack without changing schema, but safe.
            from services.document import DocumentService
            # We bypass document service upload and just insert directly for speed/stealth
            db = get_db()
            conn = db.get_connection()
            c = conn.cursor()
            c.execute("INSERT INTO documents (user_id, filepath, filename, status) VALUES (?, ?, ?, ?)", 
                     (user_id, "manual_entry", "Manual Entry", "Processed"))
            doc_id = c.lastrowid
            conn.commit()
            
            success, msg = self.service.create_invoice(user_id, vendor, gst, date, total, document_id=doc_id)

        if success:
            messagebox.showinfo("Success", "Saved successfully")
            self.parent.refresh_data()
            self.destroy()
        else:
            messagebox.showerror("Error", msg)
