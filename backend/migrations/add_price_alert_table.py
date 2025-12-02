"""
Migration script to add PriceAlert table to the database.
"""

def upgrade():
    """Create the PriceAlert table."""
    # This migration will be handled by SQLAlchemy's create_all()
    # when the application starts and detects the new model
    pass

def downgrade():
    """Drop the PriceAlert table."""
    # This migration will be handled by SQLAlchemy's drop_all()
    # when needed
    pass