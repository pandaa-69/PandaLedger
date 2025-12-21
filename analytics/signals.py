from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from portfolio.models import Transaction
from analytics.services.backfill import backfill_portfolio_history
import threading

def run_backfill_in_background(user):
    print(f"🔄 Background Backfill started for {user.username}...")
    try:
        backfill_portfolio_history(user)
        print(f"✅ Background Backfill complete for {user.username}.")
    except Exception as e:
        print(f"❌ Background Backfill failed: {e}")

@receiver(post_save, sender=Transaction)
@receiver(post_delete, sender=Transaction)
def trigger_backfill(sender, instance, **kwargs):
    """
    Automatic Trigger: Whenever a transaction is added, updated, or deleted
    (from Admin or App), rebuild the history graph for that user.
    """
    user = instance.holding.user
    
    # Run in a separate thread so the UI doesn't freeze while waiting for Yahoo
    task = threading.Thread(target=run_backfill_in_background, args=(user,))
    task.start()