import pandas as pd
from db.schema import get_db
import os
from datetime import datetime
from services.audit import get_audit_service

class ExportService:
    def __init__(self):
        self.db = get_db()
        self.audit = get_audit_service()

    def export_invoices(self, user_id, format='xlsx', output_path=None):
        conn = self.db.get_connection()
        
        query = '''
            SELECT i.id, i.vendor_name, i.gst_number, i.invoice_date, i.total_amount, d.filename, d.status
            FROM invoices i
            JOIN documents d ON i.document_id = d.id
            WHERE d.user_id = ?
        '''
        
        df = pd.read_sql_query(query, conn, params=(user_id,))
        
        if df.empty:
            return False, "No data to export"
            
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            ext = format
            output_path = os.path.join(os.path.expanduser("~"), "Downloads", f"DocFlow_Export_{timestamp}.{ext}")
            
        try:
            if format == 'xlsx':
                df.to_excel(output_path, index=False)
            elif format == 'csv':
                df.to_csv(output_path, index=False)
            else:
                return False, "Unsupported format"
                
            self.audit.log_action(user_id, "EXPORT_DATA", f"Exported {len(df)} records to {format}")
            return True, output_path
        except Exception as e:
            return False, str(e)
