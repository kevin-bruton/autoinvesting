from db.common import query_one

def get_symbol_info (symbol, account_id):
  sql = '''
    SELECT FuturesSymbols.symbol, name, exchange,  currency, tickSize, priceScale, minMovement, bigPointValue, broker, roundtrip
    FROM FuturesSymbols
    LEFT JOIN FuturesCommissions ON FuturesSymbols.symbol = FuturesCommissions.symbol
    WHERE FuturesSymbols.symbol = ?
    AND broker = (SELECT broker FROM Accounts WHERE accountId = ?)
  '''
  return query_one(sql, (symbol, account_id))
  
