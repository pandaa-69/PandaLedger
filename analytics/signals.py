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

# Global Executor: Acts as a simple "Queue".
# max_workers=1 ensures we only process ONE backfill at a time.
# If 100 users add transactions, they will form a line in memory 
# instead of crashing the server.
backfill_executor = threading.Semaphore(1) # We use semaphore logic conceptually, but Executor is better
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=1)

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
    Uses a global `ThreadPoolExecutor` (max_workers=1) to strictly serialize backfills.
    This protects the server from OOM crashes by ensuring 
    RAM usage remains constant regardless of concurrent users.
    """
    try:
        user = instance.holding.user
        
        # Submit to the queue aka ThreadPool
        # This returns immediately, so the UI is still fast.
        executor.submit(run_backfill_in_background, user)
        
    except Exception as e:
        logger.error(f"Error triggering backfill signal: {e}", exc_info=True)
