from db.schema import get_db

class AuditService:
    def __init__(self):
        self.db = get_db()

    def log_action(self, user_id, action, details=None):
        """
        Log a user action.
        """
        if not user_id:
            return # Don't log system/anon actions for now or handle differently
            
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO audit_logs (user_id, action, details)
                VALUES (?, ?, ?)
            ''', (user_id, action, details))
            conn.commit()
        except Exception as e:
            print(f"Failed to write audit log: {e}")

# Global instance for easy access
_audit_service = AuditService()

def get_audit_service():
    return _audit_service
