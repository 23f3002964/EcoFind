"""
Background task scheduler for the EcoFinds application.
Handles periodic tasks like sending auction notifications and price alerts.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from backend.utils.notifications import send_auction_ending_soon_notifications, send_auction_ended_notifications, send_price_alert_notifications
import atexit

def init_scheduler(app):
    """
    Initialize the background scheduler for periodic tasks.
    
    Args:
        app (Flask): Flask application instance
        
    Returns:
        BackgroundScheduler: The initialized scheduler instance
    """
    # Create background scheduler instance
    scheduler = BackgroundScheduler()
    
    # Add job to send notifications for auctions ending soon (runs every hour)
    scheduler.add_job(
        func=send_auction_ending_soon_notifications,
        trigger=IntervalTrigger(hours=1),  # Run every hour
        id='auction_ending_soon',
        name='Send auction ending soon notifications',
        replace_existing=True
    )
    
    # Add job to send notifications for auctions that have ended (runs every 30 minutes)
    scheduler.add_job(
        func=send_auction_ended_notifications,
        trigger=IntervalTrigger(minutes=30),  # Run every 30 minutes
        id='auction_ended',
        name='Send auction ended notifications',
        replace_existing=True
    )
    
    # Add job to check for price alerts (runs every 2 hours)
    scheduler.add_job(
        func=send_price_alert_notifications,
        trigger=IntervalTrigger(hours=2),  # Run every 2 hours
        id='price_alerts',
        name='Check and send price alert notifications',
        replace_existing=True
    )
    
    # Start the scheduler in the background
    scheduler.start()
    
    # Ensure scheduler shuts down cleanly when app exits
    atexit.register(lambda: scheduler.shutdown())
    
    # Store scheduler reference in app for potential future use
    app.scheduler = scheduler
    
    return scheduler