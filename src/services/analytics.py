from db.schema import get_db
import sqlite3
from datetime import datetime

class AnalyticsService:
    def __init__(self):
        self.db = get_db()

    def get_dashboard_stats(self, user_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Pending Docs
        cursor.execute("SELECT COUNT(*) FROM documents WHERE user_id = ? AND status = 'Pending'", (user_id,))
        stats['pending_docs'] = cursor.fetchone()[0]
        
        # Processed Docs
        cursor.execute("SELECT COUNT(*) FROM documents WHERE user_id = ? AND status = 'Processed'", (user_id,))
        stats['processed_docs'] = cursor.fetchone()[0]
        
        # Rejected (using 'Rejected' status if we had it, or just generic check)
        cursor.execute("SELECT COUNT(*) FROM documents WHERE user_id = ? AND status = 'Rejected'", (user_id,))
        stats['rejected_docs'] = cursor.fetchone()[0]
        
        # Total Revenue (sum of invoices)
        # Using a join just in case, or simple sum if ownership is validated
        # Simplification: Sum all invoices linked to user's docs
        cursor.execute('''
            SELECT SUM(i.total_amount) 
            FROM invoices i 
            JOIN documents d ON i.document_id = d.id 
            WHERE d.user_id = ?
        ''', (user_id,))
        res = cursor.fetchone()[0]
        stats['total_revenue'] = res if res else 0.0
        
        return stats

    def get_monthly_revenue(self, user_id):
        """Get revenue grouped by month for charting."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # SQLite doesn't have great date functions by default, using simple strftime
        cursor.execute('''
            SELECT strftime('%Y-%m', i.invoice_date) as month, SUM(i.total_amount)
            FROM invoices i
            JOIN documents d ON i.document_id = d.id
            WHERE d.user_id = ?
            GROUP BY month
            ORDER BY month
        ''', (user_id,))
        
        return cursor.fetchall()
