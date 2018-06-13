# modified from https://github.com/s2t2/stocks-app-py-2018/blob/master/app/robo_adviser.py

import csv
import json
import os
import pdb
import requests
from datetime import datetime
from IPython import embed

def parse_response(response_text):

    # response_text can be either a raw JSON string or an already-converted dictionary
    if isinstance(response_text, str): # if not yet converted, then:
        response_text = json.loads(response_text) # convert string to dictionary

    results = []
    time_series_daily = response_text["Time Series (Daily)"] #> a nested dictionary
    for trading_date in time_series_daily: # FYI: can loop through a dictionary's top-level keys/attributes
        prices = time_series_daily[trading_date] #> {'1. open': '101.0924', '2. high': '101.9500', '3. low': '100.5400', '4. close': '101.6300', '5. volume': '22165128'}
        result = {
            "date": trading_date,
            "open": prices["1. open"],
            "high": prices["2. high"],
            "low": prices["3. low"],
            "close": prices["4. close"],
            "volume": prices["5. volume"]
        }
        results.append(result)
    return results

def write_prices_to_file(prices=[], filename="data/prices.csv"):
    csv_filepath = os.path.join(os.path.dirname(__file__), "..", filename)
    with open(csv_filepath, "w") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["timestamp", "open", "high", "low", "close", "volume"])
        writer.writeheader()
        for d in prices:
            row = {
                "timestamp": d["date"], # change attribute name to match project requirements
                "open": d["open"],
                "high": d["high"],
                "low": d["low"],
                "close": d["close"],
                "volume": d["volume"]
            }
            writer.writerow(row)


if __name__ == '__main__': # only execute if file invoked from the command-line, not when imported into other files, like tests

    # API KEY ENVIRONMENT VARIABLE SET USING THE ECHO METHOD

    api_key = os.environ.get("ALPHAVANTAGE_API_KEY") or "OOPS. Please set an environment variable named 'ALPHAVANTAGE_API_KEY'."

    # CAPTURE USER INPUT

    symbol = input("Please input a stock ticker (e.g. 'NFLX'): ")

    # VALIDATE SYMBOL AND PREVENT UNECESSARY REQUESTS
    try:
        float(symbol)
        quit("CHECK YOUR TICKER. EXPECTING NON-NUMERIC TICKER")
    except ValueError as e:
        pass

    # ASSEMBLE REQUEST URL

    request_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"

    # ISSUE "GET" REQUEST
    print("Issuing a request")
    response = requests.get(request_url)

    # VALIDATE RESPONSE AND HANDLE ERRORS

    if "Error Messsage" in response.text:
        print("REQUEST ERROR. PLEASE TRY AGAIN. CHECK YOUR STOCK TICKER TO MAKE SURE IT IS VALID.")
        quit("Stopping the program.")

    # PARSE RESPONSE (AS LONG AS THERE ARE NO ERRORS)

    daily_prices = parse_response(response.text)

    # WRITE TO CSV

    write_prices_to_file(prices=daily_prices, filename="data/prices.csv")

    # PERFORM CALCULATIONS

    print("Here are some calculations for",symbol,":")

    print("The program was executed on:",datetime.now())

    latest_close = daily_prices[0]['close']
    latest_close = float(latest_close)
    latest_close_usd = "${0:,.2f}".format(latest_close)
    print("The latest closing price for",symbol,"is:",latest_close_usd)

    date_last = daily_prices[0]['date']
    print("The date of last data refresh was:", date_last)

    # FOLLOWING ADAPTED FROM: https://stackoverflow.com/questions/5320871/in-list-of-dicts-find-min-value-of-a-common-dict-field

    last_year = daily_prices[:252]
    last_year = [x['close'] for x in last_year]

    max_last_year = float(max(last_year))
    max_last_year = "${0:,.2f}".format(max_last_year)
    print("The 52 week high for",symbol,"is:",max_last_year)

    min_last_year = float(min(last_year))
    min_last_year = "${0:,.2f}".format(min_last_year)
    print("The 52 week low for",symbol,"is:",min_last_year)

    # FINAL RECOMMENDATION
    high_low_spread = (float(max(last_year))-float(min(last_year)))/float(min(last_year))
    if high_low_spread >= .20:
        print("Buy",symbol)
    else:
        print("Do not buy",symbol)

    print("The recommendation is based on the percent difference between the 52wk high and the 52wk low prices.",
    "If it is greater than 20%, the recommendation is buy. If it is less than 20%, the recommendation is do not buy",
    "Keep in mind, this is with the idea that with greater rism comes greater reward, and that stocks with higher volatility",
    "tend to mean revert. Therefore, this recommendation seeks to maximize return and this is done by taking on greater risk.")
