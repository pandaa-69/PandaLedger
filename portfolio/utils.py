def db_assets_classify(symbol, name):
    symbol = symbol.upper()
    name = name.upper()

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

