from db.schema import get_db
from datetime import datetime, timedelta

class LicensingService:
    def __init__(self):
        self.db = get_db()
        self._ensure_license_record()

    def _ensure_license_record(self):
        """Ensure at least one license record exists for the machine."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM license LIMIT 1")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO license (plan_type, is_active) VALUES ('Free', 1)")
            conn.commit()

    def get_current_plan(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT plan_type, expiry_date FROM license WHERE is_active = 1 ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            return {
                "plan": row['plan_type'],
                "expiry": row['expiry_date']
            }
        return {"plan": "Free", "expiry": None}

    def activate_license(self, key):
        """
        Mock activation.
        Keys starting with 'PRO-' are valid Pro licenses.
        Keys starting with 'ENT-' are Enterprise.
        """
        key = key.strip().upper()
        plan = "Free"
        
        if key.startswith("PRO-"):
            plan = "Pro"
        elif key.startswith("ENT-"):
            plan = "Enterprise"
        else:
            return False, "Invalid License Key"

        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Set expiry to 1 year from now
        expiry = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
        
        try:
            # Deactivate old
            cursor.execute("UPDATE license SET is_active = 0")
            # Insert new
            cursor.execute('''
                INSERT INTO license (license_key, plan_type, expiry_date, is_active)
                VALUES (?, ?, ?, 1)
            ''', (key, plan, expiry))
            conn.commit()
            return True, f"Activated {plan} Plan successfully!"
        except Exception as e:
            return False, str(e)

    def can_access(self, feature):
        plan_info = self.get_current_plan()
        plan = plan_info['plan']
        
        restrictions = {
            "Free": ["documents", "invoices", "workflows"],
            "Pro": ["documents", "invoices", "workflows", "analytics", "unlimited_docs"],
            "Enterprise": ["documents", "invoices", "workflows", "analytics", "unlimited_docs", "audit_logs"]
        }
        
        allowed = restrictions.get(plan, restrictions["Free"])
        return feature in allowed
