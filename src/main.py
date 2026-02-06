import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.schema import get_db
from ui.app import DocFlowApp
import logging

# Setup Logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'logs')
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, 'app.log'),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # Initialize DB
    print("Initializing Database...")
    try:
        db = get_db()
        print("Database initialized.")
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.critical(f"Database init failed: {e}")
        messagebox.showerror("Critical Error", f"Failed to initialize database: {e}")
        return

    # Start App
    print("Starting DocFlow Pro...")
    try:
        root = tk.Tk()
        app = DocFlowApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Application Error", f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
