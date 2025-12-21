from portfolio.models import Transaction, Holding
from datetime import date
from pyxirr import xirr
import pandas as pd

def calculate_portfolio_xirr(user):
    """
    Calculates the XIRR (Annualized return) for the entire portfolio
    by considering 
    Buys as negative cash flow and sells as positive cash flow
    treeating the current portfolio value as a sell today positive cash floww
    """

    # getting all the transactions of the user
    txs = Transaction.objects.filter(holding__user = user).values('date', 'type', 'quantity', 'price')

    if not txs:
        return 0.0
    
    dates = []
    amounts = []

    # processing the transactions (Cash Flows)
    for t in txs:
        total = float(t['quantity']*t['price'])
        dates.append(t['date'])


        # BUY = negative and Sell = positive outflow +
        # 

        if t['type'] == 'BUY':
            amounts.append(-total)
        else:
            amounts.append(total)

    # adding the current value of portfolio as of today treating it like a sell we pretend we sold everyting today to calculate the final return 

    holdings = Holding.objects.filter(user=user)
    current_value = sum(float(h.quantity * h.asset.last_price) for h in holdings)

    if current_value>0:
        dates.append(date.today())
        amounts.append(current_value)

    # Calculating XIRR 
    try:
        # pyxirr need a dictionary or arrays
        # we need to multiply by 100 to get the percentage

        result = xirr(dates,amounts)
        return round(result*100, 2) if result else 0.0
    except Exception as e:
        print(f"XIRR Error: {e}")
        return 0.0
    

def get_sector_split(user):
    """
    Returns the percentage allocation per sector (eg, IT 40%, Bank 30%)

    """
    holidngs = Holding.objects.filter(user=user).select_related('asset')
    sector_map = {}
    total_val = 0

    for h in holidngs:
        # we will use Type for non stocks like gold etf if sector is empty 

        val = float(h.quantity*h.asset.last_price)
        sec = h.asset.sector

        # fallback for etfs / gold which might not hav a sector

        if not sec or sec =="Other":
            sec=h.asset.asset_type

        sector_map[sec] = sector_map.get(sec,0)+val

        total_val += val

    # converting to percentage 
    if total_val == 0: return []

    return[
        {"name": k , "value": round((v/total_val)*100, 2), "total": round(v,2)} for k,v in sector_map.items()
    ]