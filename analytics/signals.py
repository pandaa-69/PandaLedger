import logging
import threading
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from portfolio.models import Transaction
from analytics.services.backfill import backfill_portfolio_history

logger = logging.getLogger(__name__)

def run_backfill_in_background(user):
    """
    Executes the portfolio history backfill process in a separate thread.
    
    This ensures that expensive calculations (fetching historical data, recalculating daily values)
    do not block the main request/response cycle for the user.
    """
    logger.info(f"🔄 Background Backfill started for user: {user.username}")
    try:
        backfill_portfolio_history(user)
        logger.info(f"✅ Background Backfill complete for user: {user.username}")
    except Exception as e:
        logger.error(f"❌ Background Backfill failed for user {user.username}: {e}", exc_info=True)

@receiver(post_save, sender=Transaction)
@receiver(post_delete, sender=Transaction)
def trigger_backfill(sender, instance, **kwargs):
    """
    Signal receiver to trigger a portfolio history recalculation whenever a Transaction is modified.
    
    Triggered on:
    - Transaction Creation (Buy/Sell)
    - Transaction Update
    - Transaction Deletion
    
    Note:
    Uses `threading.Thread` for simplicity. In a high-scale production environment, 
    this should be offloaded to a task queue like Celery or Redis Queue (RQ) 
    to prevent thread exhaustion.
    """
    try:
        user = instance.holding.user
        
        # Run in a separate thread so the UI doesn't freeze while waiting for Yahoo Finance/calculations
        task = threading.Thread(
            target=run_backfill_in_background, 
            args=(user,),
            daemon=True # Daemon threads are killed if the main process exits
        )
        task.start()
        
    except Exception as e:
        logger.error(f"Error triggering backfill signal: {e}", exc_info=True)
