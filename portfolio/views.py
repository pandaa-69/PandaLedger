from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Asset, Holding, Transaction
import json
import yfinance as yf
from datetime import date
from analytics.services.backfill import backfill_portfolio_history
# --- HELPER: SMART ASSET DETECTION 🧠 ---
def detect_asset_type(info, symbol, name):
    sType = info.get('quoteType', '').upper()
    name_upper = name.upper()
    symbol_upper = symbol.upper()

    # 1. CRYPTO
    if sType == 'CRYPTOCURRENCY' or '-USD' in symbol_upper:
        return 'CRYPTO'
    
    # 2. REITs (Check Name FIRST)
    # Catches: Mindspace REIT, Embassy Office Parks REIT
    if 'REIT' in name_upper or sType == 'REIT':
        return 'REIT'

    # 3. GOLD / SILVER
    # Catches: GOLDBEES, SILVERBEES
    if 'GOLD' in name_upper or 'SILVER' in name_upper:
        return 'GOLD'
    
    # 4. ETFs
    # Catches: MON100, NIFTYBEES, BANKBEES
    if ('ETF' in name_upper or 
        'BEES' in name_upper or 
        'MON100' in symbol_upper or
        sType == 'ETF'):
        return 'ETF'
    
    # 5. MUTUAL FUNDS
    if sType == 'MUTUALFUND' or 'FUND' in name_upper:
        return 'MF'

    # Default
    return 'STOCK'
# 1. SEARCH API
# 1. SEARCH API (Updated for Sector & Market Cap)
@login_required
def search_asset(request):
    query = request.GET.get('q', '').strip().upper()
    if not query:
        return JsonResponse([], safe=False)

    # Local Search
    assets = Asset.objects.filter(name__icontains=query) | Asset.objects.filter(symbol__icontains=query)
    results = [{"id": a.id, "symbol": a.symbol, "name": a.name, "type": a.asset_type, "price": float(a.last_price)} for a in assets[:5]]

    if len(results) < 3 and len(query) > 2:
        try:
            yahoo_symbol = f"{query}.NS" if not ("-" in query or "." in query) else query
            ticker = yf.Ticker(yahoo_symbol)
            
            # Fetch Data
            try:
                full_info = ticker.info
                price = full_info.get('currentPrice') or full_info.get('regularMarketPreviousClose')
                name = full_info.get('longName', query)
                
                # --- NEW: Get Insights ---
                sector = full_info.get('sector', 'Other')
                mcap = full_info.get('marketCap', 0)
                
                # Mcap Logic (Indian Context in Crores approx)
                mcap_cat = 'MID'
                if mcap > 200000000000: # > 20,000 Cr
                    mcap_cat = 'LARGE'
                elif mcap < 50000000000: # < 5,000 Cr
                    mcap_cat = 'SMALL'
                
            except:
                full_info = {}
                price = ticker.fast_info.last_price
                name = query
                sector = 'Other'
                mcap_cat = 'MID'

            if price and price > 0:
                detected_type = detect_asset_type(full_info, yahoo_symbol, name)
                
                new_asset = Asset.objects.create(
                    symbol=yahoo_symbol,
                    name=name,
                    last_price=price,
                    asset_type=detected_type,
                    sector=sector,                # 👈 NEW
                    market_cap_category=mcap_cat   # 👈 NEW
                )
                results.append({
                    "id": new_asset.id, 
                    "symbol": new_asset.symbol, 
                    "name": new_asset.name, 
                    "type": detected_type, 
                    "price": price
                })
        except:
            pass
            
    return JsonResponse(results, safe=False)

# 2. GET PORTFOLIO (Updated to send Sector & Cap to Frontend)
@login_required
def get_portfolio(request):
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
            "sector": h.asset.sector,               # 👈 NEW
            "market_cap_category": h.asset.market_cap_category, # 👈 NEW
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

    return JsonResponse({
        "holdings": data,
        "summary": {
            "total_value": round(total_value, 2),
            "total_invested": round(total_invested, 2),
            "total_profit": round(total_value - total_invested, 2)
        }
    })

# 3. ADD TRANSACTION
@csrf_exempt
@login_required
def add_transaction(request):
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
            # This rebuilds the graph history instantly after you add a trade.
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

# 4. DELETE TRANSACTION (Updated with Backfill)
@csrf_exempt
@login_required
def delete_transaction(request, transaction_id):
    if request.method == 'DELETE':
        try:
            tx = Transaction.objects.get(id=transaction_id, holding__user=request.user)
            holding = tx.holding
            tx.delete()
            holding.recalculate()
            
            # 👇 TRIGGER THE TIME MACHINE 🕰️
            # If you delete a trade, the past changes. We must rebuild.
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
@login_required
def get_holding_details(request, asset_id):
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