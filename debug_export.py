import pandas as pd
from db.schema import get_db
from services.export import ExportService
import sys

def debug_export():
    try:
        # Ensure data exist
        db = get_db()
        conn = db.get_connection()
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO documents (user_id, filepath, filename) VALUES (1, 'debug.pdf', 'debug.pdf')")
        c.execute("SELECT id FROM documents WHERE filename='debug.pdf'")
        doc_id = c.fetchone()[0]
        c.execute("INSERT OR IGNORE INTO invoices (document_id, vendor_name, total_amount) VALUES (?, 'Debug Vendor', 999.0)", (doc_id,))
        conn.commit()

        service = ExportService()
        success, msg = service.export_invoices(1, 'xlsx', 'debug_export_service.xlsx')
        print(f"Service Export Result: {success} - {msg}")
        
    except Exception as e:
        print(f"Export Failed Error: {e}")

if __name__ == "__main__":
    debug_export()
