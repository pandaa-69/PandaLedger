def db_assets_classify(symbol, name):
    symbol = symbol.upper()
    name = name.upper()

    if 'GOLD' in name or 'SILVER' in name or 'GOLDBEES' in symbol or 'SGB' in symbol:
        return 'GOLD'

    if 'REIT' in name:
        return 'REIT'

    if symbol.isdigit():
        return 'MF'

    if 'ETF' in name or 'BEES' in symbol or 'MON100' in symbol:
        return 'ETF'

    if '-USD' in symbol:
        return 'CRYPTO'

    return 'STOCK'