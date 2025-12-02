"""
Migration script to add missing columns to the User table.
"""

def upgrade():
    """Add missing columns to the User table."""
    # This migration will be handled by SQLAlchemy's create_all()
    # when the application starts and detects the new model
    pass

def downgrade():
    """Remove the added columns from the User table."""
    # This migration will be handled by SQLAlchemy's drop_all()
    # when needed
    pass