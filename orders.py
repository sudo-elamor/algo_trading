import json
from auth import get_smartapi
def get_symbol_token(tradingsymbol, exchange="NSE"):
    """ Fetch the correct symbol token dynamically """
    smartApi = get_smartapi()
    search_response = smartApi.searchScrip(exchange, tradingsymbol)

    if search_response.get("status"):
        return search_response["data"][0]["symboltoken"]
    else:
        print("❌ Error fetching symbol token:", search_response)
        return None

def place_order(transaction_type, tradingsymbol, quantity, price=None):
    """
    Place a buy/sell order using SmartAPI.
    
    :param transaction_type: "BUY" or "SELL"
    :param tradingsymbol: Stock symbol (e.g., "RELIANCE")
    :param symboltoken: Numeric token for the stock
    :param quantity: Number of shares
    :param price: Limit price (None for market order)
    """

    smartApi = get_smartapi()
    symboltoken = get_symbol_token(tradingsymbol)

    order_params = {
        "variety": "NORMAL",  # NORMAL, AMO, STOPLOSS
        "tradingsymbol": tradingsymbol,
        "symboltoken": symboltoken,
        "transactiontype": transaction_type,
        "exchange": "NSE",
        "ordertype": "LIMIT" if price else "MARKET",
        "producttype": "INTRADAY",  # Can be "DELIVERY", "CNC", "MARGIN"
        "duration": "DAY",
        "quantity": quantity,
        "price": price or 0,  # 0 for market order
    }

    try:
        response = smartApi.placeOrder(order_params)

        print(response)

    except Exception as e:
        print("❌ Error placing order:", str(e))

place_order(transaction_type="BUY", tradingsymbol="RELIANCE-EQ", quantity=1)