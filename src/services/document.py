import os
import shutil
from datetime import datetime
from db.schema import get_db
from services.ocr import get_ocr_service

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'uploads')

class DocumentService:
    def __init__(self):
        self.db = get_db()
        self.ocr = get_ocr_service()
        os.makedirs(UPLOAD_DIR, exist_ok=True)

    def upload_document(self, user_id, source_path):
        """
        Copy file to uploads dir, save to DB, and trigger OCR.
        """
        filename = os.path.basename(source_path)
        # Unique filename using timestamp
        clean_name = f"{int(datetime.now().timestamp())}_{filename}"
        dest_path = os.path.join(UPLOAD_DIR, clean_name)
        
        try:
            shutil.copy2(source_path, dest_path)
            
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO documents (user_id, filepath, filename, file_type, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, dest_path, filename, os.path.splitext(filename)[1], 'Pending'))
            
            doc_id = cursor.lastrowid
            conn.commit()
            
            # Audit
            from services.audit import get_audit_service
            get_audit_service().log_action(user_id, "UPLOAD_DOC", f"Uploaded: {filename}")
            
            # Auto-trigger OCR (could be async in future)
            # text = self.ocr.extract_text(dest_path)
            # For now just update status to "Uploaded"
            
            return True, doc_id
        except Exception as e:
            return False, str(e)

    def get_user_documents(self, user_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE user_id = ? ORDER BY upload_date DESC", (user_id,))
        return cursor.fetchall()

    def process_document(self, doc_id):
        """Run OCR and update status/content."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT filepath FROM documents WHERE id = ?", (doc_id,))
        row = cursor.fetchone()
        if not row:
            return False, "Document not found"
            
        filepath = row['filepath']
        text = self.ocr.extract_text(filepath)
        
        # Parse text to extract invoice data
        from services.extraction import ExtractionService
        extractor = ExtractionService()
        data = extractor.extract_invoice_data(text)
        
        # Save to Invoices Table
        cursor.execute('''
            INSERT INTO invoices (document_id, vendor_name, gst_number, invoice_date, total_amount, gst_details)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (doc_id, data['vendor_name'], data['gst_number'], data['invoice_date'], data['total_amount'], text))
        
        cursor.execute("UPDATE documents SET status = 'Processed' WHERE id = ?", (doc_id,))
        conn.commit()
        
        return True, data
