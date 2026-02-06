from db.schema import get_db
from utils.security import hash_password, verify_password
from datetime import datetime
from services.audit import get_audit_service

class AuthManager:
    def __init__(self):
        self.db = get_db()
        self.current_user = None
        self.audit = get_audit_service()

    def register_user(self, full_name, username, password, email=None, role='user'):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            pwd_hash = hash_password(password)
            cursor.execute('''
                INSERT INTO users (full_name, username, password_hash, email, role)
                VALUES (?, ?, ?, ?, ?)
            ''', (full_name, username, pwd_hash, email, role))
            user_id = cursor.lastrowid
            conn.commit()
            
            self.audit.log_action(user_id, "REGISTER", f"User registered: {username}")
            return True, "User registered successfully."
        except Exception as e:
            return False, str(e)

    def login(self, username, password):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if user and verify_password(user['password_hash'], password):
            self.current_user = dict(user)
            # Update last login
            cursor.execute("UPDATE users SET last_login = ? WHERE id = ?", (datetime.now(), user['id']))
            conn.commit()
            
            self.audit.log_action(user['id'], "LOGIN", "User logged in.")
            return True, self.current_user
        
        return False, "Invalid credentials."

    def logout(self):
        if self.current_user:
            self.audit.log_action(self.current_user['id'], "LOGOUT", "User logged out.")
        self.current_user = None

    def get_current_user(self):
        return self.current_user

    def is_admin(self):
        return self.current_user and self.current_user['role'] == 'admin'
