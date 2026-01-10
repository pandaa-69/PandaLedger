from django.core.management.base import BaseCommand
from portfolio.models import Asset

class Command(BaseCommand):
    help = 'Safely seeds the DB with 300+ Top Assets (Metadata only).'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting massive asset seeding...")

        ASSETS = [
            # ==========================================
            # Popular Indian ETFs (Nippon/Motilal Oswal)
            # ==========================================
            ("NIFTYBEES.NS", "Nippon India Nifty 50 Bees ETF", "ETF"),
            ("BANKBEES.NS", "Nippon India ETF Bank BeES", "ETF"),
            ("JUNIORBEES.NS", "Nippon India Nifty Next 50 Bees ETF", "ETF"),
            ("GOLDBEES.NS", "Nippon India ETF Gold BeES", "ETF"),
            ("SILVERBEES.NS", "Nippon India Silver ETF", "ETF"),
            ("ITBEES.NS", "Nippon India ETF Nifty IT", "ETF"),
            ("PHARMABEES.NS", "Nippon India ETF Nifty Pharma", "ETF"),
            ("PSUBNKBEES.NS", "Nippon India ETF PSU Bank BeES", "ETF"),
            ("AUTOBEES.NS", "Nippon India ETF Nifty Auto", "ETF"),
            ("INFRA.NS", "Nippon India ETF Infra BeES", "ETF"),
            ("LIQUIDBEES.NS", "Nippon India ETF Liquid BeES", "ETF"),
            ("MOM30IETF.NS", "Motilal Oswal Nifty 200 Momentum 30 ETF", "ETF"),
            ("LOWVOLIETF.NS", "Motilal Oswal S&P BSE Low Volatility ETF", "ETF"),
            ("MON100.NS", "Motilal Oswal Nasdaq 100 ETF", "ETF"),
            ("MAFANG.NS", "Mirae Asset NYSE FANG+ ETF", "ETF"),
            ("HNGSNGBEES.NS", "Nippon India ETF Hang Seng BeES", "ETF"),

            # ==========================================
            # NIFTY 50 Stocks
            # ==========================================
            ("RELIANCE.NS", "Reliance Industries Ltd", "STOCK"),
            ("TCS.NS", "Tata Consultancy Services", "STOCK"),
            ("HDFCBANK.NS", "HDFC Bank", "STOCK"),
            ("ICICIBANK.NS", "ICICI Bank", "STOCK"),
            ("INFY.NS", "Infosys", "STOCK"),
            ("BHARTIARTL.NS", "Bharti Airtel", "STOCK"),
            ("ITC.NS", "ITC Ltd", "STOCK"),
            ("SBIN.NS", "State Bank of India", "STOCK"),
            ("LICI.NS", "LIC India", "STOCK"),
            ("HINDUNILVR.NS", "Hindustan Unilever", "STOCK"),
            ("TATAMOTORS.NS", "Tata Motors", "STOCK"),
            ("LT.NS", "Larsen & Toubro", "STOCK"),
            ("HCLTECH.NS", "HCL Technologies", "STOCK"),
            ("BAJFINANCE.NS", "Bajaj Finance", "STOCK"),
            ("SUNPHARMA.NS", "Sun Pharmaceutical", "STOCK"),
            ("MARUTI.NS", "Maruti Suzuki", "STOCK"),
            ("TITAN.NS", "Titan Company", "STOCK"),
            ("ULTRACEMCO.NS", "UltraTech Cement", "STOCK"),
            ("ASIANPAINT.NS", "Asian Paints", "STOCK"),
            ("ADANIENT.NS", "Adani Enterprises", "STOCK"),
            ("ADANIPORTS.NS", "Adani Ports", "STOCK"),
            ("TATASTEEL.NS", "Tata Steel", "STOCK"),
            ("COALINDIA.NS", "Coal India", "STOCK"),
            ("NTPC.NS", "NTPC Ltd", "STOCK"),
            ("AXISBANK.NS", "Axis Bank", "STOCK"),
            ("KOTAKBANK.NS", "Kotak Mahindra Bank", "STOCK"),
            ("POWERGRID.NS", "Power Grid Corp", "STOCK"),
            ("ONGC.NS", "ONGC", "STOCK"),
            ("WIPRO.NS", "Wipro Ltd", "STOCK"),
            ("JSWSTEEL.NS", "JSW Steel", "STOCK"),
            ("GRASIM.NS", "Grasim Industries", "STOCK"),
            ("TECHM.NS", "Tech Mahindra", "STOCK"),
            ("ADANIGREEN.NS", "Adani Green Energy", "STOCK"),
            ("ADANIPOWER.NS", "Adani Power", "STOCK"),
            ("BAJAJFINSV.NS", "Bajaj Finserv", "STOCK"),
            ("NESTLEIND.NS", "Nestle India", "STOCK"),
            ("TATACONSUM.NS", "Tata Consumer Products", "STOCK"),
            ("BRITANNIA.NS", "Britannia Industries", "STOCK"),
            ("M&M.NS", "Mahindra & Mahindra", "STOCK"),
            ("DIVISLAB.NS", "Divi's Laboratories", "STOCK"),
            ("DRREDDY.NS", "Dr. Reddy's Laboratories", "STOCK"),
            ("CIPLA.NS", "Cipla", "STOCK"),
            ("APOLLOHOSP.NS", "Apollo Hospitals", "STOCK"),
            ("EICHERMOT.NS", "Eicher Motors", "STOCK"),
            ("HEROMOTOCO.NS", "Hero MotoCorp", "STOCK"),
            ("HINDALCO.NS", "Hindalco Industries", "STOCK"),
            ("LTIM.NS", "LTIMindtree", "STOCK"),
            ("SBILIFE.NS", "SBI Life Insurance", "STOCK"),
            ("HDFCLIFE.NS", "HDFC Life Insurance", "STOCK"),
            ("BPCL.NS", "Bharat Petroleum", "STOCK"),
            ("INDUSINDBK.NS", "IndusInd Bank", "STOCK"),

            # ==========================================
            # Midcaps & Trending Stocks
            # ==========================================
            ("ZOMATO.NS", "Zomato Ltd", "STOCK"),
            ("JIOFIN.NS", "Jio Financial Services", "STOCK"),
            ("PAYTM.NS", "One 97 Communications (Paytm)", "STOCK"),
            ("NYKAA.NS", "FSN E-Commerce (Nykaa)", "STOCK"),
            ("POLICYBZR.NS", "PB Fintech (PolicyBazaar)", "STOCK"),
            ("DELHIVERY.NS", "Delhivery Ltd", "STOCK"),
            ("IRFC.NS", "Indian Railway Finance Corp", "STOCK"),
            ("RVNL.NS", "Rail Vikas Nigam Ltd", "STOCK"),
            ("IRCTC.NS", "IRCTC", "STOCK"),
            ("MAZDOCK.NS", "Mazagon Dock Shipbuilders", "STOCK"),
            ("COCHINSHIP.NS", "Cochin Shipyard", "STOCK"),
            ("HAL.NS", "Hindustan Aeronautics Ltd", "STOCK"),
            ("BEL.NS", "Bharat Electronics Ltd", "STOCK"),
            ("BHEL.NS", "Bharat Heavy Electricals", "STOCK"),
            ("REC.NS", "REC Ltd", "STOCK"),
            ("PFC.NS", "Power Finance Corp", "STOCK"),
            ("VBL.NS", "Varun Beverages", "STOCK"),
            ("TRENT.NS", "Trent Ltd", "STOCK"),
            ("TATAELXSI.NS", "Tata Elxsi", "STOCK"),
            ("KPITTECH.NS", "KPIT Technologies", "STOCK"),
            ("DIXON.NS", "Dixon Technologies", "STOCK"),
            ("POLYCAB.NS", "Polycab India", "STOCK"),
            ("ASTRAL.NS", "Astral Ltd", "STOCK"),
            ("DEEPAKNTR.NS", "Deepak Nitrite", "STOCK"),
            ("SRF.NS", "SRF Ltd", "STOCK"),
            ("PIIND.NS", "PI Industries", "STOCK"),
            ("PAGEIND.NS", "Page Industries", "STOCK"),
            ("MRF.NS", "MRF Ltd", "STOCK"),
            ("BOSCHLTD.NS", "Bosch Ltd", "STOCK"),
            ("COLPAL.NS", "Colgate Palmolive", "STOCK"),
            ("PGHH.NS", "Procter & Gamble Hygiene", "STOCK"),
            ("MCDOWELL-N.NS", "United Spirits", "STOCK"),
            ("JUBLFOOD.NS", "Jubilant FoodWorks", "STOCK"),
            ("DEVYANI.NS", "Devyani International", "STOCK"),
            ("SAPPHIRE.NS", "Sapphire Foods", "STOCK"),
            ("SONACOMS.NS", "Sona BLW Precision Forgings", "STOCK"),
            ("OLECTRA.NS", "Olectra Greentech", "STOCK"),
            ("JBMA.NS", "JBM Auto", "STOCK"),
            ("SUZLON.NS", "Suzlon Energy", "STOCK"),
            ("YESBANK.NS", "Yes Bank", "STOCK"),
            ("IDEA.NS", "Vodafone Idea", "STOCK"),
            ("PNB.NS", "Punjab National Bank", "STOCK"),
            ("CANBK.NS", "Canara Bank", "STOCK"),
            ("UNIONBANK.NS", "Union Bank of India", "STOCK"),
            ("BANKBARODA.NS", "Bank of Baroda", "STOCK"),
            ("IDFCFIRSTB.NS", "IDFC First Bank", "STOCK"),
            ("FEDERALBNK.NS", "Federal Bank", "STOCK"),
            ("AUBANK.NS", "AU Small Finance Bank", "STOCK"),
            ("MUTHOOTFIN.NS", "Muthoot Finance", "STOCK"),
            ("MANAPPURAM.NS", "Manappuram Finance", "STOCK"),
            ("CHOLAFIN.NS", "Cholamandalam Investment", "STOCK"),
            ("SHRIRAMFIN.NS", "Shriram Finance", "STOCK"),
            ("L&TFH.NS", "L&T Finance Holdings", "STOCK"),
            ("POONAWALLA.NS", "Poonawalla Fincorp", "STOCK"),
            ("ANGELONE.NS", "Angel One", "STOCK"),
            ("BSE.NS", "BSE Ltd", "STOCK"),
            ("MCX.NS", "Multi Commodity Exchange", "STOCK"),
            ("CDSL.NS", "CDSL", "STOCK"),
            ("CAMS.NS", "CAMS", "STOCK"),
            ("IEX.NS", "Indian Energy Exchange", "STOCK"),
            ("BSOFT.NS", "Birlasoft", "STOCK"),
            ("PERSISTENT.NS", "Persistent Systems", "STOCK"),
            ("COFORGE.NS", "Coforge", "STOCK"),
            ("LTTS.NS", "L&T Technology Services", "STOCK"),
            ("MPHASIS.NS", "Mphasis", "STOCK"),
            
            # ==========================================
            # US Tech Stocks
            # ==========================================
            ("AAPL", "Apple Inc", "STOCK"),
            ("MSFT", "Microsoft Corp", "STOCK"),
            ("GOOGL", "Alphabet Inc (Google)", "STOCK"),
            ("AMZN", "Amazon.com", "STOCK"),
            ("TSLA", "Tesla Inc", "STOCK"),
            ("NVDA", "NVIDIA Corp", "STOCK"),
            ("META", "Meta Platforms", "STOCK"),
            ("NFLX", "Netflix", "STOCK"),
            ("AMD", "Advanced Micro Devices", "STOCK"),
            ("INTC", "Intel Corp", "STOCK"),
            ("PLTR", "Palantir Technologies", "STOCK"),
            ("COIN", "Coinbase Global", "STOCK"),
            ("UBER", "Uber Technologies", "STOCK"),
            ("ABNB", "Airbnb Inc", "STOCK"),
            ("DIS", "Walt Disney Co", "STOCK"),
            ("SBUX", "Starbucks Corp", "STOCK"),
            ("NKE", "Nike Inc", "STOCK"),
            ("KO", "Coca-Cola Co", "STOCK"),
            ("PEP", "PepsiCo Inc", "STOCK"),
            ("MCD", "McDonald's Corp", "STOCK"),
            ("V", "Visa Inc", "STOCK"),
            ("MA", "Mastercard Inc", "STOCK"),
            ("JPM", "JPMorgan Chase", "STOCK"),
            
            # ==========================================
            # Top 20 Cryptocurrencies
            # ==========================================
            ("BTC-USD", "Bitcoin", "CRYPTO"),
            ("ETH-USD", "Ethereum", "CRYPTO"),
            ("SOL-USD", "Solana", "CRYPTO"),
            ("BNB-USD", "Binance Coin", "CRYPTO"),
            ("XRP-USD", "XRP", "CRYPTO"),
            ("ADA-USD", "Cardano", "CRYPTO"),
            ("DOGE-USD", "Dogecoin", "CRYPTO"),
            ("AVAX-USD", "Avalanche", "CRYPTO"),
            ("TRX-USD", "TRON", "CRYPTO"),
            ("DOT-USD", "Polkadot", "CRYPTO"),
            ("MATIC-USD", "Polygon", "CRYPTO"),
            ("LTC-USD", "Litecoin", "CRYPTO"),
            ("SHIB-USD", "Shiba Inu", "CRYPTO"),
            ("LINK-USD", "Chainlink", "CRYPTO"),
            ("UNI-USD", "Uniswap", "CRYPTO"),
            ("ATOM-USD", "Cosmos", "CRYPTO"),
            ("XLM-USD", "Stellar", "CRYPTO"),
            ("XMR-USD", "Monero", "CRYPTO"),
        ]

        # COUNTERS
        added = 0
        skipped = 0

        # Fast seed loop (No API calls)
        for symbol, name, cat in ASSETS:
            # Check DB first. If missing, create with defaults.
            obj, created = Asset.objects.get_or_create(
                symbol=symbol,
                defaults={
                    'name': name,
                    'asset_type': cat,
                    'last_price': 0.0, # 0.0 ensures we don't block on network
                    'market_cap_category': 'MID', # Default, update later
                    'sector': 'Unknown'
                }
            )
            if created:
                added += 1
            else:
                skipped += 1

        self.stdout.write(self.style.SUCCESS(f"Done. Added {added} new assets. Skipped {skipped} existing."))