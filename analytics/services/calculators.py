import logging
from portfolio.models import Transaction, Holding
from datetime import date
from pyxirr import xirr
import pandas as pd

logger = logging.getLogger(__name__)

def calculate_portfolio_xirr(user):
    """
    Calculates the Extended Internal Rate of Return (XIRR) for the user's portfolio.

    XIRR is a more accurate measure of return than simple absolute return because it
    accounts for the timing of cash flows (multiple buys/sells).

    Methodology:
    1. Treat BUY transactions as negative cash flows (outflow).
    2. Treat SELL transactions as positive cash flows (inflow).
    3. Treat current portfolio value as a positive cash flow occurring 'today' (unrealized gain).

    Args:
        user (User): The user for whom to calculate XIRR.

    Returns:
        float: XIRR percentage (e.g., 12.5 for 12.5%). Returns 0.0 on error or insufficient data.
    """
    try:
        # Fetch relevant fields only for performance
        txs = Transaction.objects.filter(holding__user=user).values('date', 'type', 'quantity', 'price')

        if not txs:
            return 0.0
        
        dates = []
        amounts = []

        # 1. Process Historical Cash Flows
        for t in txs:
            total = float(t['quantity'] * t['price'])
            dates.append(t['date'])

            if t['type'] == 'BUY':
                amounts.append(-total) # Money leaving pocket
            else:
                amounts.append(total)  # Money entering pocket

        # 2. Add Terminal Value (Current Portfolio Value)
        # We pretend we liquidated everything today to mark the end of the calculation period
        holdings = Holding.objects.filter(user=user)
        current_value = sum(float(h.quantity * h.asset.last_price) for h in holdings)

        if current_value > 0:
            dates.append(date.today())
            amounts.append(current_value)

        # 3. Calculate XIRR
        # pyxirr is highly optimized (Rust-based)
        result = xirr(dates, amounts)
        
        # Convert to percentage (e.g., 0.12 -> 12.0)
        return round(result * 100, 2) if result else 0.0

    except Exception as e:
        logger.error(f"XIRR Calculation Error for {user.username}: {e}")
        return 0.0
    

def get_sector_split(user):
    """
    Calculates the sectoral allocation of the portfolio.

    Fallback Logic:
    - If a stock has a defined sector (e.g., 'IT', 'Finance'), use it.
    - If sector is missing or 'Other' (common for ETFs/Gold), use the asset_type (e.g., 'ETF', 'GOLD').

    Returns:
        list[dict]: A list of sectors with their percentage weight and total value.
        Example: [{"name": "IT", "value": 40.0, "total": 50000}, ...]
    """
    holdings = Holding.objects.filter(user=user).select_related('asset')
    sector_map = {}
    total_val = 0

    for h in holdings:
        val = float(h.quantity * h.asset.last_price)
        sec = h.asset.sector

        # Fallback for assets like Gold/ETFs that might not have a traditional sector
        if not sec or sec == "Other":
            sec = h.asset.asset_type

        sector_map[sec] = sector_map.get(sec, 0) + val
        total_val += val

    if total_val == 0:
        return []

    # Format result as a list of dictionaries for the frontend graph
    return [
        {
            "name": k, 
            "value": round((v / total_val) * 100, 2), 
            "total": round(v, 2)
        } 
        for k, v in sector_map.items()
    ]