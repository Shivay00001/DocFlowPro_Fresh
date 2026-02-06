from db.schema import get_db
from datetime import datetime
from services.audit import get_audit_service

class InvoiceService:
    def __init__(self):
        self.db = get_db()
        self.audit = get_audit_service()

    def create_invoice(self, user_id, vendor_name, gst_number, invoice_date, total_amount, document_id=None):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # If manually created, document_id is None. 
            # ideally we link it to a 'Manual Entry' document placeholder or allow NULL.
            # Schema allows NULL for document_id (checked previously).
            
            cursor.execute('''
                INSERT INTO invoices (document_id, vendor_name, gst_number, invoice_date, total_amount)
                VALUES (?, ?, ?, ?, ?)
            ''', (document_id, vendor_name, gst_number, invoice_date, total_amount))
            
            inv_id = cursor.lastrowid
            conn.commit()
            
            self.audit.log_action(user_id, "CREATE_INVOICE", f"Created Manual Invoice #{inv_id}")
            return True, inv_id
        except Exception as e:
            return False, str(e)

    def update_invoice(self, user_id, invoice_id, vendor_name, gst_number, invoice_date, total_amount):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE invoices 
                SET vendor_name = ?, gst_number = ?, invoice_date = ?, total_amount = ? 
                WHERE id = ?
            ''', (vendor_name, gst_number, invoice_date, total_amount, invoice_id))
            conn.commit()
            
            self.audit.log_action(user_id, "UPDATE_INVOICE", f"Updated Invoice #{invoice_id}")
            return True, "Updated successfully"
        except Exception as e:
            return False, str(e)

    def delete_invoice(self, user_id, invoice_id):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Optional: Delete associated document if it's orphan? 
            # For now, just delete the invoice record.
            
            cursor.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
            conn.commit()
            
            self.audit.log_action(user_id, "DELETE_INVOICE", f"Deleted Invoice #{invoice_id}")
            return True, "Deleted successfully"
        except Exception as e:
            return False, str(e)
