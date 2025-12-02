"""
Migration script to add missing columns to the User table.
"""

def upgrade():
    """Add missing columns to the User table."""
    import sqlite3
    import os
    
    # Connect to the database
    db_path = os.path.join('instance', 'appDB.sqlite3')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Add email_verified column
    try:
        cursor.execute("ALTER TABLE user ADD COLUMN email_verified BOOLEAN DEFAULT 0")
        print("Added email_verified column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e).lower():
            print(f"Error adding email_verified column: {e}")
        else:
            print("email_verified column already exists")
    
    # Add phone_verified column
    try:
        cursor.execute("ALTER TABLE user ADD COLUMN phone_verified BOOLEAN DEFAULT 0")
        print("Added phone_verified column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e).lower():
            print(f"Error adding phone_verified column: {e}")
        else:
            print("phone_verified column already exists")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()

def downgrade():
    """In SQLite, columns cannot be easily dropped, so this is a no-op."""
    print("Downgrade not supported for SQLite - columns cannot be dropped easily")
    pass

if __name__ == "__main__":
    upgrade()