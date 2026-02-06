from db.schema import get_db

class WorkflowService:
    def __init__(self):
        self.db = get_db()

    def create_approval_request(self, doc_id, requester_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO approval_requests (document_id, requester_id, status)
                VALUES (?, ?, 'Pending')
            ''', (doc_id, requester_id))
            conn.commit()
            return True, "Request created"
        except Exception as e:
            return False, str(e)

    def get_pending_approvals(self, user_id=None):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # If user_id is admin, show all. If normal user, show only theirs?
        # For this demo, let's assume 'user_id' is the APPROVER.
        # Since we don't have complex role mapping, we'll show ALL pending requests for now
        # akin to a shared inbox.
        
        query = '''
            SELECT ar.id, d.filename, u.full_name as requester, ar.created_at, ar.status, i.total_amount
            FROM approval_requests ar
            JOIN documents d ON ar.document_id = d.id
            JOIN users u ON ar.requester_id = u.id
            LEFT JOIN invoices i ON d.id = i.document_id
            WHERE ar.status = 'Pending'
        '''
        cursor.execute(query)
        return cursor.fetchall()

    def update_approval_status(self, request_id, status, comment):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE approval_requests 
                SET status = ?, reviewer_comment = ?
                WHERE id = ?
            ''', (status, comment, request_id))
            conn.commit()
            return True, "Updated successfully"
        except Exception as e:
            return False, str(e)
