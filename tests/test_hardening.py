from services.audit import get_audit_service
from services.export import ExportService
from db.schema import get_db

def test_hardening():
    print("--- Testing Product Hardening Features ---")
    
    db = get_db()
    conn = db.get_connection()
    c = conn.cursor()
    
    # 1. Audit Logging
    audit = get_audit_service()
    audit.log_action(1, "TEST_ACTION", "Testing Audit Log")
    
    c.execute("SELECT * FROM audit_logs WHERE action='TEST_ACTION'")
    entry = c.fetchone()
    print(f"Audit Entry: {dict(entry)}")
    assert entry['action'] == "TEST_ACTION"
    print("Audit Log Logic Passed.")
    
    # 2. Export (Mocking data if none exists)
    # Ensure at least one invoice
    c.execute("SELECT count(*) FROM invoices")
    if c.fetchone()[0] == 0:
        print("Creating dummy invoice for export test...")
        # Create dummy doc & invoice
        c.execute("INSERT INTO documents (user_id, filepath, filename) VALUES (1, 'test.pdf', 'test.pdf')")
        doc_id = c.lastrowid
        c.execute("INSERT INTO invoices (document_id, vendor_name, total_amount) VALUES (?, 'Test Vendor', 500.0)", (doc_id,))
        conn.commit()

    export = ExportService()
    success, result = export.export_invoices(1, 'csv', 'test_export.csv')
    print(f"Export CSV Result: Success={success}, Msg={result}")
    
    if not success:
        print("!!! Export Failed. Checking DB...")
        c.execute("SELECT * FROM documents WHERE user_id=1")
        print(f"Docs for User 1: {c.fetchall()}")
        c.execute("SELECT * FROM invoices")
        print(f"All Invoices: {c.fetchall()}")
    
    assert success == True
    
    import os
    if os.path.exists('test_export.csv'):
        print("Export File Created.")
        os.remove('test_export.csv')
    else:
        print("Export File NOT Found.")

if __name__ == "__main__":
    test_hardening()
