import yfinance as yf
import pandas as pd
from datetime import date, timedelta
from portfolio.models import Transaction
from analytics.models import PortfolioSnapshot
from django.db import transaction

def backfill_portfolio_history(user):
    """
    Reconstructs portfolio history using Pandas.
    FIXED: Handles column name matching correctly for .NS symbols.
    """
    # 1. Fetch Transactions
    txs = list(Transaction.objects.filter(holding__user=user).select_related('holding__asset').order_by('date'))
    if not txs:
        return

    # 2. Determine Time Range
    start_date = txs[0].date
    # Safety: Limit to 15 years max
    min_date = date.today() - timedelta(days=365 * 15)
    if start_date < min_date:
        start_date = min_date

    end_date = date.today()
    
    # 3. Identify Assets
    asset_symbols = list(set(t.holding.asset.symbol for t in txs))
    print(f"📉 Fetching history for {len(asset_symbols)} assets from {start_date}...")

    # 4. Batch Fetch Prices
    try:
        # Ensure we request the exact symbols as they appear in the DB
        # If DB has 'ITC', we ask for 'ITC.NS'. If DB has 'ITC.NS', we ask for 'ITC.NS'.
        yahoo_request_map = {s: (s if ('.' in s or '-' in s) else f"{s}.NS") for s in asset_symbols}
        yahoo_symbols = list(yahoo_request_map.values())
        
        market_data = yf.download(yahoo_symbols, start=start_date, end=end_date + timedelta(days=1), progress=False)['Close']
    except Exception as e:
        print(f"❌ Yahoo Error: {e}")
        return

    # 5. Build Holdings Timeline (The "What I Owned" Grid)
    all_dates = pd.date_range(start=start_date, end=end_date, freq='D')
    holdings_df = pd.DataFrame(0.0, index=all_dates, columns=asset_symbols)
    invested_df = pd.DataFrame(0.0, index=all_dates, columns=['invested_cash'])

    for tx in txs:
        if tx.date < start_date: continue
        tx_date = pd.Timestamp(tx.date)
        if tx_date in holdings_df.index:
            sym = tx.holding.asset.symbol
            qty = float(tx.quantity)
            cash_flow = float(tx.quantity * tx.price)

            if tx.type == 'BUY':
                holdings_df.loc[tx_date, sym] += qty
                invested_df.loc[tx_date, 'invested_cash'] += cash_flow
            elif tx.type == 'SELL':
                holdings_df.loc[tx_date, sym] -= qty
                invested_df.loc[tx_date, 'invested_cash'] -= cash_flow

    daily_holdings = holdings_df.cumsum()
    daily_invested = invested_df.cumsum()

    # 6. Align Prices & Calculate Value
    # Reindex Yahoo data to match our timeline (fills weekends/holidays)
    price_data = market_data.reindex(all_dates).ffill()

    # 👇 CRITICAL FIX: Ensure columns match DB symbols exactly
    # -------------------------------------------------------
    # Yahoo might return 'ITC.NS', 'AAPL', etc.
    # Our holdings_df uses DB symbols. We need to map them if they differ.
    
    # Create a clean dataframe for prices with DB symbols as columns
    aligned_prices = pd.DataFrame(index=all_dates)
    
    for db_symbol in asset_symbols:
        yahoo_symbol = yahoo_request_map[db_symbol]
        
        # Check if Yahoo gave us this column
        if yahoo_symbol in price_data.columns:
            aligned_prices[db_symbol] = price_data[yahoo_symbol]
        elif len(asset_symbols) == 1 and isinstance(price_data, pd.Series):
             # Handle single-asset case where yfinance returns a Series, not DataFrame
            aligned_prices[db_symbol] = price_data
        elif len(asset_symbols) == 1 and len(price_data.columns) == 1:
             # Handle single-asset case where it returns a 1-col DataFrame
            aligned_prices[db_symbol] = price_data.iloc[:, 0]
            
    # Now multiply (Columns act as keys, so they must match!)
    daily_value = (daily_holdings * aligned_prices).sum(axis=1)

    # 7. Prepare Database Objects
    snapshots = []
    for day, value in daily_value.items():
        if pd.isna(value) or value <= 0: continue
        
        invested = daily_invested.loc[day, 'invested_cash']
        snapshots.append(PortfolioSnapshot(
            user=user,
            date=day.date(),
            total_value=round(value, 2),
            invested_value=round(invested, 2)
        ))

    # 8. Save
    print(f"💾 Saving {len(snapshots)} snapshots...")
    with transaction.atomic():
        PortfolioSnapshot.objects.filter(user=user).delete()
        PortfolioSnapshot.objects.bulk_create(snapshots)
    
    print("✅ Backfill Complete.")