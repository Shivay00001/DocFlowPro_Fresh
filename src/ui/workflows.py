import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from services.workflow import WorkflowService

class WorkflowView(tk.Frame):
    def __init__(self, master, app_controller):
        super().__init__(master, bg="#f0f2f5")
        self.app = app_controller
        self.service = WorkflowService()
        self.pack(fill=tk.BOTH, expand=True)
        
        self._create_ui()
        self.refresh()

    def _create_ui(self):
        header = tk.Frame(self, bg="#f0f2f5")
        header.pack(fill=tk.X, pady=(0, 20))
        tk.Label(header, text="Approval Workflows", font=("Segoe UI", 20, "bold"), bg="#f0f2f5").pack(side=tk.LEFT)
        tk.Button(header, text="Refresh", command=self.refresh).pack(side=tk.RIGHT)

        # Tab layout (Pending vs History, keeping simple for now with just Pending)
        container = tk.Frame(self, bg="white", padx=20, pady=20)
        container.pack(fill=tk.BOTH, expand=True)

        tk.Label(container, text="Pending Requests", font=("Segoe UI", 12, "bold"), bg="white").pack(anchor="w", pady=(0, 10))

        # Treeview
        columns = ("ID", "Document", "Requester", "Date", "Amount", "Status")
        self.tree = ttk.Treeview(container, columns=columns, show="headings", height=10)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Action Buttons
        actions = tk.Frame(container, bg="white", pady=10)
        actions.pack(fill=tk.X)
        
        tk.Button(actions, text="Approve Selected", bg="#2ecc71", fg="white", command=self.approve_request).pack(side=tk.LEFT, padx=5)
        tk.Button(actions, text="Reject Selected", bg="#e74c3c", fg="white", command=self.reject_request).pack(side=tk.LEFT, padx=5)

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        requests = self.service.get_pending_approvals(self.app.auth_manager.get_current_user()['id'])
        for req in requests:
            # req keys correspond to query in service
            self.tree.insert("", tk.END, values=(req[0], req[1], req[2], req[3], f"₹{req[5] or 0}", req[4]))

    def approve_request(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a request.")
            return
            
        req_id = self.tree.item(selected[0])['values'][0]
        # In real app, maybe add comment dialog
        success, msg = self.service.update_approval_status(req_id, "Approved", "Approved via Dashboard")
        if success:
            messagebox.showinfo("Success", "Request Approved.")
            self.refresh()
        else:
            messagebox.showerror("Error", msg)

    def reject_request(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a request.")
            return

        req_id = self.tree.item(selected[0])['values'][0]
        reason = simpledialog.askstring("Reject", "Reason for rejection:")
        if reason:
            success, msg = self.service.update_approval_status(req_id, "Rejected", reason)
            if success:
                messagebox.showinfo("Success", "Request Rejected.")
                self.refresh()
            else:
                messagebox.showerror("Error", msg)
