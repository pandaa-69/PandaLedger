from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.management import call_command
from .models import Asset, Holding, Transaction
import json
import yfinance as yf
from datetime import date
from analytics.services.backfill import backfill_portfolio_history
from django.utils import timezone
from datetime import timedelta
import requests

def detect_asset_type(info, symbol, name):
    sType = info.get('quoteType', '').upper()
    name_upper = name.upper()
    symbol_upper = symbol.upper()

    if sType == 'CRYPTOCURRENCY' or '-USD' in symbol_upper: return 'CRYPTO'
    if 'REIT' in name_upper or sType == 'REIT': return 'REIT'
    if 'GOLD' in name_upper or 'SILVER' in name_upper: return 'GOLD'
    if ('ETF' in name_upper or 'BEES' in name_upper or 'MON100' in symbol_upper or sType == 'ETF'): return 'ETF'
    if sType == 'MUTUALFUND' or 'FUND' in name_upper: return 'MF'
    return 'STOCK'


# 1. SEARCH API (Prioritizes DB for MFs)
def search_asset(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    query = request.GET.get('q', '').strip().upper()
    if not query: return JsonResponse([], safe=False)

    # 1. Local Search (This will now find the 40k seeded MFs!)
    assets = Asset.objects.filter(name__icontains=query) | Asset.objects.filter(symbol__icontains=query)
    # Increased limit to 10 to show more MF options
    results = [{"id": a.id, "symbol": a.symbol, "name": a.name, "type": a.asset_type, "price": float(a.last_price)} for a in assets[:10]]

    # 2. If DB has low results (e.g. US Stocks), ask Yahoo
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
        except Exception as e:
            pass # Yahoo failed, just return DB results
            
    return JsonResponse(results, safe=False)


# HYBRID UPDATE ENGINE (Yahoo + MFAPI)---
def update_live_prices(holdings):
    """
    Yahoo for Stocks/Crypto. MFAPI.in for Indian Mutual Funds.
    """
    cooldown_time = timezone.now() - timedelta(minutes=10)
    
    yahoo_assets = []
    yahoo_symbols = []
    mf_assets = []

    for h in holdings:
        # Update if stale OR price is 0
        if h.asset.updated_at < cooldown_time or h.asset.last_price == 0:
            # Is it a numeric code  if its like "118778"  MFAPI
            if h.asset.symbol.isdigit():
                mf_assets.append(h.asset)
            else:
                yahoo_assets.append(h.asset)
                yahoo_symbols.append(h.asset.symbol)

    if not yahoo_assets and not mf_assets:
        print("All assets are fresh. Skipping.")
        return

    print(f"Updating: {len(yahoo_assets)} via Yahoo, {len(mf_assets)} via MFAPI...")

    # --- 1. YAHOO FINANCE BATCH FETCH ---
    if yahoo_assets:
        try:
            tickers = yf.Tickers(" ".join(yahoo_symbols))
            for asset in yahoo_assets:
                try:
                    latest_price = tickers.tickers[asset.symbol].fast_info.last_price
                    if latest_price and latest_price > 0:
                        asset.last_price = latest_price
                        asset.updated_at = timezone.now()
                except Exception as e:
                    print(f"Yahoo Failed {asset.symbol}: {e}")
        except Exception as e:
            print(f"Yahoo Batch Failed: {e}")

    # --- 2. MFAPI.IN FETCH ---
    if mf_assets:
        for asset in mf_assets:
            try:
                response = requests.get(f"https://api.mfapi.in/mf/{asset.symbol}")
                if response.status_code == 200:
                    data = response.json()
                    if data.get('data'):
                        latest_nav = float(data['data'][0]['nav']) # 0 is latest date
                        asset.last_price = latest_nav
                        asset.updated_at = timezone.now()
                        print(f"MFAPI Updated {asset.symbol}: ₹{latest_nav}")
            except Exception as e:
                print(f"MFAPI Failed {asset.symbol}: {e}")

    # --- 3. SAVE ALL UPDATES ---
    all_updates = yahoo_assets + mf_assets
    if all_updates:
        Asset.objects.bulk_update(all_updates, ['last_price', 'updated_at'])
        print(f"Saved {len(all_updates)} prices to DB.")

# 2. GET PORTFOLIO
def get_portfolio(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    # 1. Get User's Holdings
    holdings = Holding.objects.filter(user=request.user).select_related('asset')
    
    # 2.UPDATE PRICES BEFORE CALCULATING 
    if holdings.exists():
        update_live_prices(holdings)
        # Refresh holdings from DB to get the new prices we just saved
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


# 3. ADD TRANSACTION
def add_transaction(request):
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
            
            # 👇 TRIGGER THE TIME MACHINE 🕰️
            print("🔄 Triggering History Backfill...")
            try:
                backfill_portfolio_history(request.user)
                print("✅ History Updated!")
            except Exception as e:
                print(f"⚠️ Backfill Failed: {e}")

            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({'error': 'POST method required'}, status=405)


# 4. DELETE TRANSACTION
def delete_transaction(request, transaction_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    if request.method == 'DELETE':
        try:
            tx = Transaction.objects.get(id=transaction_id, holding__user=request.user)
            holding = tx.holding
            tx.delete()
            holding.recalculate()
            
            # 👇 TRIGGER THE TIME MACHINE 🕰️
            print("🔄 Triggering History Backfill...")
            try:
                backfill_portfolio_history(request.user)
                print("✅ History Updated!")
            except Exception as e:
                print(f"⚠️ Backfill Failed: {e}")

            return JsonResponse({"status": "success"})
        except Transaction.DoesNotExist:
            return JsonResponse({"error": "Transaction not found"}, status=404)
    return JsonResponse({'error': 'DELETE method required'}, status=405)


# 5. GET HOLDING DETAILS
def get_holding_details(request, asset_id):
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


# 6 SEED TRIGGER so that i can trigger db with this to add the assest first time 
def seed_db_view(request):
    if not request.user.is_superuser: 
        return HttpResponse("Unauthorized: Admins only.", status=403)
    
    try:
        call_command('seed_assets')
        return HttpResponse("✅ Seed command executed successfully! Assets have been added to DB.")
    except Exception as e:
        return HttpResponse(f"❌ Error seeding DB: {str(e)}", status=500)
    

# 7. ROOT / WAKE UP VIEW
def wake_up(request):
    return HttpResponse("<h1>🐼 PandaLedger Backend is Awake!</h1><p>Status: Active</p>")

# 6. 🔓 SECRET SEED TRIGGER (Updated to include MFs)
def seed_db_view(request):
    if not request.user.is_superuser: 
        return HttpResponse("Unauthorized: Admins only.", status=403)
    
    try:
        # Seed Standard Assets (Stocks, Crypto, Gold)
        call_command('seed_assets') 
        
        # Seed Mutual Funds (The New Logic)
        call_command('seed_mfs')
        
        return HttpResponse("✅ Database Seeded! Stocks & Mutual Funds are ready.")
    except Exception as e:
        return HttpResponse(f"❌ Error seeding DB: {str(e)}", status=500)