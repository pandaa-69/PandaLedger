from django.core.management.base import BaseCommand
from portfolio.models import Asset
import yfinance as yf

class Command(BaseCommand):
    help = 'Seeds the database with popular Assets (Stocks, Crypto, Gold, MFs)'

    def handle(self, *args, **kwargs):
        self.stdout.write("🌱 Starting Asset Seeding...")

        ASSETS = [
            # --- STOCKS (Nifty/Sensex Mix) ---
            ("RELIANCE.NS", "Reliance Industries", "STOCK"),
            ("TCS.NS", "Tata Consultancy Services", "STOCK"),
            ("HDFCBANK.NS", "HDFC Bank", "STOCK"),
            ("INFY.NS", "Infosys", "STOCK"),
            ("ICICIBANK.NS", "ICICI Bank", "STOCK"),
            ("TATAMOTORS.NS", "Tata Motors", "STOCK"),
            ("ZOMATO.NS", "Zomato", "STOCK"),
            
            # --- MUTUAL FUNDS (Common ones - Symbols vary, using approximations) ---
            # Yahoo symbols for MFs are tricky. Let's use some ETFs as proxies for now 
            # or you can find exact MF tickers later.
            ("NIFTYBEES.NS", "Nippon India Nifty 50 Bees ETF", "MF"),
            ("GOLDBEES.NS", "Nippon India Gold BEES ETF", "MF"),
            ("SILVERBEES.NS", "Nippon India Silver ETF", "MF"),
            ("0P0000XW8F.BO", "Parag Parikh Flexi Cap Fund", "MF"), # Actual Ticker
            
            # --- CRYPTO ---
            ("BTC-USD", "Bitcoin", "CRYPTO"),
            ("ETH-USD", "Ethereum", "CRYPTO"),
            ("SOL-USD", "Solana", "CRYPTO"),

            # --- COMMODITIES (Global) ---
            ("GC=F", "Gold Futures", "GOLD"),
            ("SI=F", "Silver Futures", "GOLD"),
        ]

        for symbol, name, cat in ASSETS:
            if not Asset.objects.filter(symbol=symbol).exists():
                try:
                    self.stdout.write(f"fetching {name}...")
                    ticker = yf.Ticker(symbol)
                    price = ticker.fast_info.last_price
                    
                    Asset.objects.create(
                        symbol=symbol,
                        name=name,
                        asset_type=cat,
                        last_price=price if price else 0.0
                    )
                    self.stdout.write(self.style.SUCCESS(f"✅ Added {name}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Failed {name}: {e}"))
            else:
                self.stdout.write(f"⚠️ {name} already exists.")

        self.stdout.write(self.style.SUCCESS("🚀 Seeding Complete!"))