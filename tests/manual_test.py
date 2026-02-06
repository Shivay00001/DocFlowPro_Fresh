import sys
import os
import shutil

# Setup Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(PROJECT_ROOT, 'src'))

from auth.manager import AuthManager
from services.document import DocumentService
from db.schema import get_db

def test_initialization_flow():
    print("--- Starting DocFlow Pro Initialization Test ---")
    
    # 1. Setup DB
    db = get_db()
    
    # Clean up test user if exists
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username = 'testuser'")
    conn.commit()
    
    # 2. Test Registration
    print("Testing Registration...")
    auth = AuthManager()
    success, msg = auth.register_user("Test User", "testuser", "password123", role="admin")
    if not success:
        print(f"Registration Failed: {msg}")
        return
    print("Registration Successful.")
    
    # 3. Test Login
    print("Testing Login...")
    success, user = auth.login("testuser", "password123")
    if not success:
        print(f"Login Failed: {user}")
        return
    print(f"Login Successful: Welcome {user['full_name']}")
    
    # 4. Test Document Upload
    print("Testing Document Upload...")
    
    # Create a dummy file
    dummy_path = os.path.join(PROJECT_ROOT, 'test_doc.txt')
    with open(dummy_path, 'w') as f:
        f.write("Invoice #12345\nTotal: $500.00")
        
    doc_service = DocumentService()
    success, doc_id = doc_service.upload_document(user['id'], dummy_path)
    
    if success:
        print(f"Upload Successful. Doc ID: {doc_id}")
    else:
        print(f"Upload Failed: {doc_id}")
        return
        
    # 5. Verify in DB
    docs = doc_service.get_user_documents(user['id'])
    if len(docs) > 0:
        print(f"Verification Successful: Found {len(docs)} documents for user.")
        print(f"Latest Doc: {docs[0]['filename']} - Status: {docs[0]['status']}")
    else:
        print("Verification Failed: No documents found in DB.")
        
    # Cleanup
    if os.path.exists(dummy_path):
        os.remove(dummy_path)
    
    print("--- Test Complete ---")

if __name__ == "__main__":
    test_initialization_flow()
