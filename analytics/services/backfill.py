import logging
import yfinance as yf
import pandas as pd
import requests
from datetime import date, datetime, timedelta
from django.db import transaction
from portfolio.models import Transaction
from analytics.models import PortfolioSnapshot

logger = logging.getLogger(__name__)

def backfill_portfolio_history(user):
    """
    Reconstructs the entire historical value of a user's portfolio.

    Strategy (Hybrid Engine):
    1. Fetches all historical transactions for the user.
    2. Identifies all unique assets.
        - Stocks/Crypto -> Yahoo Finance
        - Mutual Funds -> MFAPI (India)
    3. Downloads historical price data for the entire date range.
    4. Replays changes in holdings day-by-day (Cumulative Sum).
    5. Calculates Daily Value = (Daily Holdings * Daily Price).
    6. Stores the result as daily `PortfolioSnapshot` records.

    Args:
        user (User): The user instance to backfill data for.
    """
    try:
        # 1. Fetch Transactions
        txs = list(Transaction.objects.filter(holding__user=user)
                   .select_related('holding__asset')
                   .order_by('date'))
        
        if not txs:
            logger.info(f"No transactions found for user {user.username}. Skipping backfill.")
            return

        # 2. Determine Time Range
        start_date = txs[0].date
        min_date = date.today() - timedelta(days=365 * 30) # 30-year safety cap
        if start_date < min_date:
            start_date = min_date
        end_date = date.today()
        
        # 3. Identify Assets & Split Buckets
        asset_symbols = list(set(t.holding.asset.symbol for t in txs))
        
        yahoo_symbols = []
        mf_codes = []
        
        # Logic: If it's all digits, it's MFAPI (AMFI Code). Otherwise Yahoo.
        for sym in asset_symbols:
            if sym.isdigit():
                mf_codes.append(sym)
            else:
                # Append .NS for Indian stocks if missing (Assumption: NSE)
                if '.' not in sym and '-' not in sym:
                    yahoo_symbols.append(f"{sym}.NS")
                else:
                    yahoo_symbols.append(sym)

        logger.info(f" Fetching history for {user.username}: {len(yahoo_symbols)} Yahoo, {len(mf_codes)} MFAPI symbols...")

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
                logger.error(f"Yahoo History Error: {e}", exc_info=True)

        # --- B. MFAPI FETCH ---
        if mf_codes:
            for code in mf_codes:
                try:
                    # Fetch history from MFAPI
                    res = requests.get(f"https://api.mfapi.in/mf/{code}", timeout=10)
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
                            logger.info(f"MFAPI History fetched for: {code}")
                except Exception as e:
                    logger.warning(f"MFAPI History Failed for {code}: {e}")

        # 5. Build Holdings Timeline
        holdings_df = pd.DataFrame(0.0, index=all_dates, columns=asset_symbols)
        invested_df = pd.DataFrame(0.0, index=all_dates, columns=['invested_cash'])

        for tx in txs:
            if tx.date < start_date: continue
            tx_date = pd.Timestamp(tx.date)
            
            # Ensure proper indexing even if tx_date is slightly out of range due to timezone
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
        
        # Create an aligned dataframe for calculation
        daily_value = pd.DataFrame(0.0, index=all_dates, columns=daily_holdings.columns)
        
        # Multiply only matching columns to avoid key errors
        common_assets = list(set(daily_holdings.columns) & set(price_df.columns))
        for col in common_assets:
            daily_value[col] = daily_holdings[col] * price_df[col]
        
        total_daily_value = daily_value.sum(axis=1)

        # 7. Save Snapshots
        snapshots = []
        for day, value in total_daily_value.items():
            # Skip invalid or empty days
            if pd.isna(value) or value <= 0: continue
            
            invested = daily_invested.loc[day, 'invested_cash']
            snapshots.append(PortfolioSnapshot(
                user=user,
                date=day.date(),
                total_value=round(value, 2),
                invested_value=round(invested, 2)
            ))

        with transaction.atomic():
            # Nuclear option: Clear old history and replace with fresh accurate data
            PortfolioSnapshot.objects.filter(user=user).delete()
            PortfolioSnapshot.objects.bulk_create(snapshots)
        
        logger.info(f"Hybrid Backfill Complete for {user.username}: {len(snapshots)} snapshots created.")

    except Exception as e:
        logger.error(f"Critical error in backfill_portfolio_history for {user.username}: {e}", exc_info=True)
