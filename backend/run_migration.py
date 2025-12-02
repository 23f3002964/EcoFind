"""
Script to run database migrations.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

def run_migration():
    """Run all database migrations."""
    # Import here to avoid context issues
    from app import createApp
    from backend.models import db
    
    app = createApp()
    
    with app.app_context():
        print("Running database migrations...")
        try:
            # Create all tables (including any new ones and updating existing ones)
            db.create_all()
            print("All migrations completed successfully!")
        except Exception as e:
            print(f"Error running migrations: {e}")
            return False
    
    return True

if __name__ == "__main__":
    run_migration()