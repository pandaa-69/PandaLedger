import logging
import json
import requests , zoneinfo
from datetime import date, timedelta , datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.management import call_command
from django.utils import timezone
import yfinance as yf

from .models import Asset, Holding, Transaction
from analytics.services.backfill import backfill_portfolio_history

logger = logging.getLogger(__name__)

def detect_asset_type(info, symbol, name):
    """
    Detect the asset type based on Yahoo Finance metadata.
    """
    sType = info.get('quoteType', '').upper()
    name_upper = name.upper()
    symbol_upper = symbol.upper()

    # Mutual funds (AMFI code)
    if symbol.isdigit():
        return 'MF'
    
    # Crypto
    if "-USD" in symbol:
        return 'CRYPTO'
    
    # ETFS
    if "ETF" in name or "Exchange traded fund" in name :
        if 'GOLD' in name or 'SILVER' in name:
            return 'GOLD'
        return 'ETF'
    
    # Sovereign / Physical Gold
    if 'SGB' in symbol or name.startswith('SOVEREIGN GOLD'):
        return 'GOLD'
    
    # REITs
    if 'REIT' in name :
        return 'REIT'
    
    return 'STOCK'


# Asset Search API
def search_asset(request):
    """
    Search for assets by name or symbol.
    Prioritizes local DB results (especially for seeded Mutual Funds).
    Falls back to Yahoo Finance for US Stocks/Crypto if local results are sparse.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    query = request.GET.get('q', '').strip().upper()
    if not query: return JsonResponse([], safe=False)

    # Local Search
    assets = Asset.objects.filter(name__icontains=query) | Asset.objects.filter(symbol__icontains=query)
    results = [{"id": a.id, "symbol": a.symbol, "name": a.name, "type": a.asset_type, "price": float(a.last_price)} for a in assets[:10]]

    # Fallback to Yahoo Finance if results are low
    if len(results) < 3 and len(query) > 2:
        try:
            yahoo_symbol = f"{query}.NS" if not ("-" in query or "." in query) else query
            ticker = yf.Ticker(yahoo_symbol)
            
            try:
                full_info = ticker.info
                price = full_info.get('currentPrice') or full_info.get('regularMarketPreviousClose')
                name = full_info.get('longName', query)
                sector = full_info.get('sector', 'Other')
                mcap = full_info.get('marketCap', 0)
                mcap_cat = 'LARGE' if mcap > 200000000000 else 'MID' if mcap > 50000000000 else 'SMALL'
            except:
                full_info = {}
                price = ticker.fast_info.last_price
                name = query
                sector = 'Other'
                mcap_cat = 'MID'

            if price and price > 0:
                detected_type = detect_asset_type(full_info, yahoo_symbol, name)
                new_asset = Asset.objects.create(
                    symbol=yahoo_symbol, name=name, last_price=price,
                    asset_type=detected_type, sector=sector, market_cap_category=mcap_cat
                )
                results.append({"id": new_asset.id, "symbol": new_asset.symbol, "name": new_asset.name, "type": detected_type, "price": price})
        except Exception:
            pass # Yahoo failed, return partial DB results
            
    return JsonResponse(results, safe=False)


# Threading Helper
def fetch_mf_price(asset):
    """
    Fetch a single Mutual Fund price from MFAPI.in.
    Designed to run in a thread pool.
    """
    try:
        # 5 second timeout to prevent blocking
        response = requests.get(f"https://api.mfapi.in/mf/{asset.symbol}", timeout=3)
        if response.status_code == 200:
            data = response.json()
            if data.get('data'):
                latest_nav = float(data['data'][0]['nav']) # 0 is latest date
                return asset, latest_nav
    except Exception as e:
        logger.error(f"MFAPI Failed {asset.symbol}: {e}")
    return asset, None


# Price Update Engine
def update_live_prices(holdings):
    """
    Update asset prices using a hybrid strategy:
    - Yahoo Finance (Batch) for Stocks/Crypto
    - MFAPI.in (Parallel Threads) for Mutual Funds
    """
    ist = zoneinfo.ZoneInfo('Asia/Kolkata')  #to get the timezone stamp of india

    now_utc = timezone.now() #the system timezone in UTC
    stock_cooldown_time = now_utc - timedelta(minutes=5)
    # mf_cooldown_time = now - timedelta(hours=21) ( not need removed)
    
    # if we set a direct delta then a bug may apear becuase if suppose a user updated the price of mf at 23:10 pm and a timer for 21 is set from that time then the next day the price wont get updated for the whole day to fix this we need to make sure we check the date only like if date is greater than date then we run the mf update price 

    yahoo_assets = []
    yahoo_symbols = []
    mf_assets = []

    # Filter Assets requiring update
    for h in holdings:
        asset = h.asset
        is_pricing_missing = asset.last_price == 0

        if asset.symbol.isdigit():  # MF request
             # Define "start of today" in IST
            midnight_ist = now_utc.astimezone(ist).replace(
                hour=0, minute=0, second=0, microsecond=0
            )

            # Refresh needed if:
            # - price missing
            # - last update happened before today's midnight IST
            last_update_ist = asset.updated_at.astimezone(ist)

            # Compare "Indian Days" in ist not UTC 
            if is_pricing_missing or last_update_ist<midnight_ist:
                mf_assets.append(asset)
        else:
            # Stock/Crypto request
            if is_pricing_missing or asset.updated_at < stock_cooldown_time:
                yahoo_assets.append(asset)
                yahoo_symbols.append(asset.symbol)
        
    if not yahoo_assets and not mf_assets:
        logger.info("All assets are fresh. Skipping update.")
        return

    logger.info(f"Updating: {len(yahoo_assets)} via Yahoo, {len(mf_assets)} via MFAPI parallel...")
    updated_assets = []

    # 1. Yahoo Finance (Batch Fetch)
    if yahoo_assets:
        try:
            tickers = yf.Tickers(" ".join(yahoo_symbols))
            for asset in yahoo_assets:
                try:
                    latest_price = tickers.tickers[asset.symbol].fast_info.last_price
                    if latest_price and latest_price > 0:
                        asset.last_price = latest_price
                        asset.updated_at = timezone.now()
                        updated_assets.append(asset)
                except Exception:
                   logger.warning(f"Failed to fetch {asset.symbol}")
        except Exception as e:
            logger.error(f"Yahoo Batch Failed: {e}")

    # 2. MFAPI.IN (Parallel Threads)
    if mf_assets:
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_asset = {executor.submit(fetch_mf_price, asset): asset for asset in mf_assets}
            
            for future in as_completed(future_to_asset):
                asset, price = future.result()
                if price:
                    asset.last_price = price
                    asset.updated_at = timezone.now()
                    updated_assets.append(asset)
                    logger.info(f"MFAPI Updated {asset.symbol}: {price}")

    # Bulk Save
    if updated_assets:
        Asset.objects.bulk_update(updated_assets, ['last_price', 'updated_at'])
        logger.info(f"Saved {len(updated_assets)} prices to DB.")

# Get Portfolio API
def get_portfolio(request):
    """
    Retrieve the user's portfolio with live calculations.
    Triggers a price update if data is stale.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    # Get User's Holdings
    holdings = Holding.objects.filter(user=request.user).select_related('asset')
    
    # Update prices if needed
    if holdings.exists():
        update_live_prices(holdings)
        # Refresh from DB
        holdings = Holding.objects.filter(user=request.user).select_related('asset')

    data = []
    total_value = 0
    total_invested = 0
    
    for h in holdings:
        current_val = h.current_value()
        invested_val = float(h.quantity * h.avg_buy_price)
        profit = current_val - invested_val
        profit_pct = (profit / invested_val * 100) if invested_val > 0 else 0
            
        data.append({
            "id": h.asset.id,
            "symbol": h.asset.symbol,
            "name": h.asset.name,
            "type": h.asset.asset_type,
            "sector": h.asset.sector,
            "market_cap_category": h.asset.market_cap_category,
            "qty": float(h.quantity),
            "avg_price": float(h.avg_buy_price),
            "current_price": float(h.asset.last_price),
            "current_value": current_val,
            "invested_value": round(invested_val, 2),
            "profit": round(profit, 2),
            "profit_pct": round(profit_pct, 2)
        })
        
        total_value += current_val
        total_invested += invested_val

    total_profit = total_value - total_invested
    total_profit_pct = (total_profit/total_invested*100) if total_invested > 0 else 0

    return JsonResponse({
        "holdings": data,
        "summary": {
            "total_value": round(total_value, 2),
            "total_invested": round(total_invested, 2),
            "total_profit": round(total_profit, 2),
            "total_profit_pct": round(total_profit_pct, 2)
        }
    })


# Add Transaction API
def add_transaction(request):
    """
    Record a new transaction (Buy/Sell).
    Triggers an asynchronous historical backfill.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            asset = Asset.objects.get(id=data['asset_id'])
            holding, created = Holding.objects.get_or_create(user=request.user, asset=asset)
            
            Transaction.objects.create(
                holding=holding,
                type=data['type'], 
                quantity=data['qty'],
                price=data['price'],
                date=data.get('date', date.today())
            )
            
            # Trigger History Backfill
            logger.info("Triggering History Backfill...")
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({'error': 'POST method required'}, status=405)


# Delete Transaction API
def delete_transaction(request, transaction_id):
    """
    Remove a transaction and recalculate the holding.
    Triggers an asynchronous historical backfill.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    if request.method == 'DELETE':
        try:
            tx = Transaction.objects.get(id=transaction_id, holding__user=request.user)
            holding = tx.holding
            tx.delete()
            holding.recalculate()
            
            # Trigger History Backfill
            logger.info("Triggering History Backfill...")
            return JsonResponse({"status": "success"})
        except Transaction.DoesNotExist:
            return JsonResponse({"error": "Transaction not found"}, status=404)
    return JsonResponse({'error': 'DELETE method required'}, status=405)


# Get Holding Details API
def get_holding_details(request, asset_id):
    """
    Retrieve detailed transaction history for a specific holding.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    try:
        holding = Holding.objects.get(user=request.user, asset_id=asset_id)
        transactions = holding.transactions.all().order_by('-date')
        
        tx_data = [{
            "id": t.id, "type": t.type, "qty": float(t.quantity),
            "price": float(t.price), "date": t.date, "total": float(t.quantity * t.price)
        } for t in transactions]
        
        return JsonResponse({
            "symbol": holding.asset.symbol,
            "name": holding.asset.name,
            "avg_price": float(holding.avg_buy_price),
            "total_qty": float(holding.quantity),
            "current_price": float(holding.asset.last_price),
            "current_value": holding.current_value(),
            "transactions": tx_data
        })
    except Holding.DoesNotExist:
        return JsonResponse({"error": "Holding not found"}, status=404)


# Root View
def wake_up(request):
    """
    Simple health check view.
    """
    return HttpResponse("<h1>🐼 PandaLedger Backend is Awake!</h1><p>Status: Active</p>")

# Secret Seed Trigger
def seed_db_view(request):
    """
    Admin-only endpoint to trigger database seeding.
    """
    if not request.user.is_superuser: 
        return HttpResponse("Unauthorized: Admins only.", status=403)
    
    try:
        # Seed Standard Assets (Stocks, Crypto, Gold)
        call_command('seed_assets') 
        
        # Seed Mutual Funds
        call_command('seed_mfs')
        
        return HttpResponse("Database Seeded! Stocks & Mutual Funds are ready.")
    except Exception as e:
        logger.error(f"Error seeding DB: {e}")
        return HttpResponse(f"Error seeding DB: {str(e)}", status=500)
    
def classify_asset_view(request):
    if not request.user.is_superuser:
        return HttpResponse("Unauthorised: Admins only", status = 403)
    
    try :
        call_command('reclassify_asset')
        return HttpResponse("DB asset classification commpleted")
    except Exception as e:
        logger.error(f"Error classifying the assets: {str(e)}", status = 500)
        
        return HttpResponse(f"Error classifying the assets: {str(e)}", status = 500)