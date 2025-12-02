"""
Notification utility functions for the EcoFinds application.
"""

from backend.models import Notification, db

def send_notification(user_id, title, message, related_product_id=None, related_bid_id=None):
    """
    Send a notification to a user.
    
    Args:
        user_id (int): ID of the user to notify
        title (str): Title of the notification
        message (str): Message content
        related_product_id (int, optional): Related product ID
        related_bid_id (int, optional): Related bid ID
        
    Returns:
        Notification: The created notification object
    """
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        related_product_id=related_product_id,
        related_bid_id=related_bid_id
    )
    
    db.session.add(notification)
    db.session.commit()
    
    return notification

def send_auction_ending_soon_notifications():
    """
    Send notifications to bidders when auctions are about to end.
    This function should be called periodically by a background task.
    """
    from backend.models import Product, Bid
    from datetime import datetime, timedelta
    
    # Find auctions ending in the next 24 hours that haven't sent notifications yet
    soon_ending_auctions = Product.query.filter(
        Product.is_auction == True,
        Product.auction_end_time <= datetime.utcnow() + timedelta(hours=24),
        Product.auction_end_time > datetime.utcnow()
    ).all()
    
    for auction in soon_ending_auctions:
        # Get all bidders for this auction
        bids = Bid.query.filter_by(product_id=auction.id).all()
        bidder_ids = set(bid.bidder_id for bid in bids)
        
        # Send notification to each bidder
        for bidder_id in bidder_ids:
            send_notification(
                user_id=bidder_id,
                title="Auction ending soon!",
                message=f"The auction for '{auction.title}' is ending in 24 hours. Place your final bid now!",
                related_product_id=auction.id
            )

def send_auction_ended_notifications():
    """
    Send notifications when auctions have ended.
    This function should be called periodically by a background task.
    """
    from backend.models import Product, Bid
    from datetime import datetime
    
    # Find auctions that ended in the last hour and haven't sent notifications yet
    recently_ended_auctions = Product.query.filter(
        Product.is_auction == True,
        Product.auction_end_time <= datetime.utcnow(),
        Product.auction_end_time > datetime.utcnow() - timedelta(hours=1)
    ).all()
    
    for auction in recently_ended_auctions:
        # Get winning bidder
        winning_bid = Bid.query.filter_by(
            product_id=auction.id, 
            amount=auction.current_bid
        ).first()
        
        # Notify seller
        send_notification(
            user_id=auction.seller_id,
            title="Your auction has ended",
            message=f"Your auction for '{auction.title}' has ended. The winning bid was ${auction.current_bid}.",
            related_product_id=auction.id
        )
        
        # Notify winning bidder
        if winning_bid:
            send_notification(
                user_id=winning_bid.bidder_id,
                title="Congratulations! You've won an auction",
                message=f"You've won the auction for '{auction.title}' with a bid of ${auction.current_bid}.",
                related_product_id=auction.id,
                related_bid_id=winning_bid.id
            )
        
        # Notify other bidders
        other_bids = Bid.query.filter(
            Bid.product_id == auction.id,
            Bid.id != (winning_bid.id if winning_bid else None)
        ).all()
        
        for bid in other_bids:
            send_notification(
                user_id=bid.bidder_id,
                title="Auction you bid on has ended",
                message=f"The auction for '{auction.title}' has ended. Unfortunately, your bid was not the winning bid.",
                related_product_id=auction.id
            )