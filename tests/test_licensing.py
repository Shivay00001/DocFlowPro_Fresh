from services.licensing import LicensingService
from db.schema import get_db

def test_licensing():
    print("--- Testing Licensing Service ---")
    
    # Reset License table
    db = get_db()
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM license")
    conn.commit()
    
    service = LicensingService() # Should auto-create Free
    
    # 1. Check Default
    plan = service.get_current_plan()
    print(f"Default Plan: {plan['plan']}")
    assert plan['plan'] == "Free"
    assert service.can_access("invoices") == True
    assert service.can_access("analytics") == False
    
    # 2. Activate Invalid
    success, msg = service.activate_license("XYZ-123")
    print(f"Invalid Activation: {success} - {msg}")
    assert success == False
    
    # 3. Activate Pro
    success, msg = service.activate_license("PRO-DEMO-KEY")
    print(f"Pro Activation: {success} - {msg}")
    assert success == True
    
    # 4. Check Pro Access
    plan = service.get_current_plan()
    print(f"New Plan: {plan['plan']} (Exp: {plan['expiry']})")
    assert plan['plan'] == "Pro"
    assert service.can_access("analytics") == True
    
    print("Licensing Logic Passed.")

if __name__ == "__main__":
    test_licensing()
