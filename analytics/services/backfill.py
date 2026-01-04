import yfinance as yf
import pandas as pd
import requests
from datetime import date, datetime, timedelta
from portfolio.models import Transaction
from analytics.models import PortfolioSnapshot
from django.db import transaction

def backfill_portfolio_history(user):
    """
    Reconstructs portfolio history using Hybrid Engine (Yahoo + MFAPI).
    """
    # 1. Fetch Transactions
    txs = list(Transaction.objects.filter(holding__user=user).select_related('holding__asset').order_by('date'))
    if not txs:
        return

    # 2. Determine Time Range
    start_date = txs[0].date
    min_date = date.today() - timedelta(days=365 * 30) # Safety cap
    if start_date < min_date:
        start_date = min_date
    end_date = date.today()
    
    # 3. Identify Assets & Split Buckets
    asset_symbols = list(set(t.holding.asset.symbol for t in txs))
    
    yahoo_symbols = []
    mf_codes = []
    
    # Logic: If it's all digits, it's MFAPI. Otherwise Yahoo.
    for sym in asset_symbols:
        if sym.isdigit():
            mf_codes.append(sym)
        else:
            # Fix yahoo symbols if needed (e.g. ITC -> ITC.NS)
            if '.' not in sym and '-' not in sym:
                yahoo_symbols.append(f"{sym}.NS")
            else:
                yahoo_symbols.append(sym)

    print(f"📉 Fetching history: {len(yahoo_symbols)} Yahoo, {len(mf_codes)} MFAPI...")

    # 4. Fetch Prices (Hybrid)
    all_dates = pd.date_range(start=start_date, end=end_date, freq='D')
    price_df = pd.DataFrame(index=all_dates)

    # --- A. YAHOO FETCH ---
    if yahoo_symbols:
        try:
            # Download close prices
            yf_data = yf.download(yahoo_symbols, start=start_date, end=end_date + timedelta(days=1), progress=False, auto_adjust=True)['Close']
            
            # Normalize YF data structure (Series -> DataFrame if single asset)
            if isinstance(yf_data, pd.Series):
                yf_data = yf_data.to_frame(name=yahoo_symbols[0])
            
            # Merge into main price dataframe
            # We need to map back to original DB symbols if we added .NS
            for db_sym in asset_symbols:
                if db_sym.isdigit(): continue # Skip MFs here
                
                yf_sym = f"{db_sym}.NS" if ('.' not in db_sym and '-' not in db_sym) else db_sym
                
                if yf_sym in yf_data.columns:
                    price_df[db_sym] = yf_data[yf_sym]
        except Exception as e:
            print(f"❌ Yahoo History Error: {e}")

    # --- B. MFAPI FETCH ---
    if mf_codes:
        for code in mf_codes:
            try:
                # Fetch history from MFAPI
                res = requests.get(f"https://api.mfapi.in/mf/{code}")
                if res.status_code == 200:
                    data = res.json().get('data', [])
                    # Convert list of dicts to DataFrame
                    mf_df = pd.DataFrame(data)
                    if not mf_df.empty:
                        # Parse dates (DD-MM-YYYY) and NAV
                        mf_df['date'] = pd.to_datetime(mf_df['date'], format='%d-%m-%Y')
                        mf_df['nav'] = mf_df['nav'].astype(float)
                        mf_df.set_index('date', inplace=True)
                        
                        # Reindex to match our master timeline
                        mf_df = mf_df.reindex(all_dates).ffill()
                        
                        # Add to master price DF
                        price_df[code] = mf_df['nav']
                        print(f"✅ MFAPI History: {code}")
            except Exception as e:
                print(f"⚠️ MFAPI History Failed {code}: {e}")

    # 5. Build Holdings Timeline
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

    # 6. Calculate Value
    # Forward fill missing prices (holidays/weekends)
    price_df = price_df.ffill()
    
    # Calculate Daily Value (Holdings * Price)
    daily_value = pd.DataFrame(index=all_dates)
    
    # Multiply matching columns
    for col in daily_holdings.columns:
        if col in price_df.columns:
            daily_value[col] = daily_holdings[col] * price_df[col]
    
    total_daily_value = daily_value.sum(axis=1)

    # 7. Save Snapshots
    snapshots = []
    for day, value in total_daily_value.items():
        if pd.isna(value) or value <= 0: continue
        
        invested = daily_invested.loc[day, 'invested_cash']
        snapshots.append(PortfolioSnapshot(
            user=user,
            date=day.date(),
            total_value=round(value, 2),
            invested_value=round(invested, 2)
        ))

    with transaction.atomic():
        PortfolioSnapshot.objects.filter(user=user).delete()
        PortfolioSnapshot.objects.bulk_create(snapshots)
    
    print(f"✅ Hybrid Backfill Complete: {len(snapshots)} snapshots.")