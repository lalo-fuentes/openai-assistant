import json
import yfinance as yf

from datetime import date

# functions schemas

ftools = [{
    "type": "function",
    "function": {
        "name": "get_stock_price",
        "description": "Useful when you want to get the closing price of a stock between two dates.",
        "parameters": {
        "type": "object",
        "properties": {
            "ticker": {"type": "string", "description": "The stock ticker symbol"},
            "start_date": {"type": "string", "description": "The first date to fetch data (YYYY-MM-DD)"},
            "end_date": {"type": "string", "description": "The last date to fetch data + 1 day (YYYY-MM-DD)"}
        },
        "required": ["ticker", "start_date", "end_date"]
        }
    }
    },
    {
    "type": "function",
    "function": {
        "name": "get_todays_date",
        "description": "Useful when you want to know today's date. Useful when the user asks for data from a relative date, like: last price, current price, last week price, last month price, etc.",
        "parameters": {
        "type": "object",
        "properties": {}
        }
    }
}]

def get_stock_price(ticker, start_date, end_date):
    ticker_data = yf.Ticker(ticker) 
    data = ticker_data.history(period="1d", start=start_date, end=end_date)
    data_list = []
    for i in range(len(data)):
        data_list.append({"date": data.index[i].strftime("%Y-%m-%d"), "price": data.iloc[i]["Close"], "currency": ticker_data.info["currency"]})
    return json.dumps(data_list)

def get_todays_date():
    # Get todays date
    today = date.today()
    # Convert date to ISO 8601 chain format
    today_iso = today.isoformat()
    # return a JSON object date 
    return json.dumps({"today": today_iso})

# ---------------------------------------------------------------------------
