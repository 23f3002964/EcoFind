"""
Background task scheduler for the EcoFinds application.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from backend.utils.notifications import send_auction_ending_soon_notifications, send_auction_ended_notifications
import atexit

def init_scheduler(app):
    """
    Initialize the background scheduler.
    
    Args:
        app (Flask): Flask application instance
    """
    # Create scheduler
    scheduler = BackgroundScheduler()
    
    # Add jobs
    scheduler.add_job(
        func=send_auction_ending_soon_notifications,
        trigger=IntervalTrigger(hours=1),  # Run every hour
        id='auction_ending_soon',
        name='Send auction ending soon notifications',
        replace_existing=True
    )
    
    scheduler.add_job(
        func=send_auction_ended_notifications,
        trigger=IntervalTrigger(minutes=30),  # Run every 30 minutes
        id='auction_ended',
        name='Send auction ended notifications',
        replace_existing=True
    )
    
    # Start the scheduler
    scheduler.start()
    
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
    
    # Store scheduler in app for potential future use
    app.scheduler = scheduler
    
    return scheduler