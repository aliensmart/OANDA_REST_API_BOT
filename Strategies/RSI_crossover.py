import datetime as dt
from pyti.relative_strength_index import relative_strength_index as rsi
import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.trades as trades
import oandapyV20.endpoints.positions as positions
import pandas as pd
import matplotlib.pyplot as plt
import time
import os
from pyti.relative_strength_index import relative_strength_index as rsi

#initiating API connection and defining trade parameters
token = os.environ.get("OANDA_DEMO_API")

client = oandapyV20.API(access_token=token,environment="practice")
account_id = "101-001-14058319-001"

#defining strategy parameters
pairs = ['EUR_USD','GBP_USD', 'AUD_USD', 'USD_JPY', 'EUR_JPY'] #currency pairs to be included in the strategy
#pairs = ['EUR_JPY','USD_JPY','AUD_JPY','AUD_USD','AUD_NZD','NZD_USD']
pos_size = 2000 #max capital allocated/position size for any currency pair
rsi_periods = 14
upper_rsi = 70.0
lower_rsi = 30.0
timeframe = "m15"

def candles(instrument):
    params = {"count": 800,"granularity": "H1"} #granularity can be in seconds S5 - S30, minutes M1 - M30, hours H1 - H12, days D, weeks W or months M
    candles = instruments.InstrumentsCandles(instrument=instrument,params=params)
    client.request(candles)
    ohlc_dict = candles.response["candles"]
    ohlc = pd.DataFrame(ohlc_dict)
    ohlc_df = ohlc.mid.dropna().apply(pd.Series)
    ohlc_df["volume"] = ohlc["volume"]
    ohlc_df.index = ohlc["time"]
    ohlc_df = ohlc_df.apply(pd.to_numeric)
    return ohlc_df

def market_order(instrument,units,sl):
    """units can be positive or negative, stop loss (in pips) added/subtracted to price """  
    account_id = "101-001-14058319-001"
    data = {
            "order": {
            "price": "",
            "stopLossOnFill": {
            "trailingStopLossOnFill": "GTC",
            "distance": str(sl)
                              },
            "timeInForce": "FOK",
            "instrument": str(instrument),
            "units": str(units),
            "type": "MARKET",
            "positionFill": "DEFAULT"
                    }
            }
    r = orders.OrderCreate(accountID=account_id, data=data)
    client.request(r)
          # (m1,m5,m15,m30,H1,H2,H3,H4,H6,H8,D1,W1,M1)



# This function places a market order in the direction BuySell, "B" = Buy, "S" = Sell, uses symbol, amount, stop, limit
def enter(BuySell, currency):

    if BuySell == "S":
        try:
            market_order(currency,-1*pos_size,0.1)
            print("New short position initiated for ", currency)
        except:
            print("   Error Opening Short Trade.")
            
    elif BuySell == "B":
        try:
            market_order(currency,pos_size,0.1)
            print("New long position initiated for ", currency)
        except:
            print("   Error Opening Long Trade.")


# This function closes all positions that are in the direction BuySell, "B" = Close All Buy Positions, "S" = Close All Sell Positions, uses symbol
def exit(BuySell, currency):
    posit = positions.PositionDetails(accountID=account_id, instrument=currency)
    client.request(posit)
    open_pos = posit.response["position"]
    long_short = {}
    long_short["long"] = open_pos["long"]["units"]
    long_short["short"] = open_pos["short"]["units"]
    
    if BuySell == "S":
        try:
            data_short = {
            "shortUnits": "ALL"}
            close_posit = positions.PositionClose(accountID=account_id, instrument=currency, data=data_short)
            client.request(close_posit)
            print("All Short positions closed for ", currency)
        except:
            print("   Error Closing Trade short for .", currency)
            
    if BuySell == "B":
        try:
            data_long = {
            "longUnits": "ALL"}
            close_posit = positions.PositionClose(accountID=account_id, instrument=currency, data=data_long)
            client.request(close_posit)
            print("All long positions closed for ", currency)
        except:
            print("   Error Closing Trade. ", currency)


# Returns true if stream1 crossed over stream2 in most recent candle, stream2 can be integer/float or data array
def crossesOver(stream1, stream2):
    # If stream2 is an int or float, check if stream1 has crossed over that fixed number
    if isinstance(stream2, int) or isinstance(stream2, float):
        if stream1[len(stream1)-1] <= stream2:
            return False
        else:
            if stream1[len(stream1)-2] > stream2:
                return False
            elif stream1[len(stream1)-2] < stream2:
                return True
            else:
                x = 2
                while stream1[len(stream1)-x] == stream2:
                    x = x + 1
                if stream1[len(stream1)-x] < stream2:
                    return True
                else:
                    return False
    # Check if stream1 has crossed over stream2
    else:
        if stream1[len(stream1)-1] <= stream2[len(stream2)-1]:
            return False
        else:
            if stream1[len(stream1)-2] > stream2[len(stream2)-2]:
                return False
            elif stream1[len(stream1)-2] < stream2[len(stream2)-2]:
                return True
            else:
                x = 2
                while stream1[len(stream1)-x] == stream2[len(stream2)-x]:
                    x = x + 1
                if stream1[len(stream1)-x] < stream2[len(stream2)-x]:
                    return True
                else:
                    return False

df = candles("EUR_USD")
df["rsi"] = rsi(df['c'], rsi_periods)

# Returns true if stream1 crossed under stream2 in most recent candle, stream2 can be integer/float or data array
def crossesUnder(stream1, stream2):
    # If stream2 is an int or float, check if stream1 has crossed under that fixed number
    if isinstance(stream2, int) or isinstance(stream2, float):
        if stream1[len(stream1)-1] >= stream2:
            return False
        else:
            if stream1[len(stream1)-2] < stream2:
                return False
            elif stream1[len(stream1)-2] > stream2:
                return True
            else:
                x = 2
                while stream1[len(stream1)-x] == stream2:
                    x = x + 1
                if stream1[len(stream1)-x] > stream2:
                    return True
                else:
                    return False
    # Check if stream1 has crossed under stream2
    else:
        if stream1[len(stream1)-1] >= stream2[len(stream2)-1]:
            return False
        else:
            if stream1[len(stream1)-2] < stream2[len(stream2)-2]:
                return False
            elif stream1[len(stream1)-2] > stream2[len(stream2)-2]:
                return True
            else:
                x = 2
                while stream1[len(stream1)-x] == stream2[len(stream2)-x]:
                    x = x + 1
                if stream1[len(stream1)-x] > stream2[len(stream2)-x]:
                    return True
                else:
                    return False

    
# Returns number of Open Positions for symbol in the direction BuySell, returns total number of both Buy and Sell positions if no direction is specified
def countOpenTrades(BuySell, currency):
    counter = 0
    posit = positions.PositionDetails(accountID=account_id, instrument=currency)
    client.request(posit)
    open_pos = posit.response["position"]
    long_short = {}
    long_short["long"] = open_pos["long"]["units"]
    long_short["short"] = open_pos["short"]["units"]
    
    if BuySell == "S":
        if long_short["short"] !=0:
            counter+=1
            
    if BuySell == "B":
        if long_short["long"] !=0:
            counter+=1
            
    return counter


# This function is run every time a candle closes
def Update(currency, rsi_period, upper_rsi, lower_rsi):
    print(str(dt.datetime.now()) + "     " + timeframe + " Bar Closed - Running Update Function...")
    
    df = candles(currency)

    # Calculate Indicators
    df["rsi"] = rsi(df['c'], rsi_periods)
    iRSI = rsi(df['c'], rsi_periods)

    # Print Price/Indicators
    print("Close Price: " + str(df['c'][-1]))
    print("RSI: " + str(iRSI[len(iRSI)-1]))

    # TRADING LOGIC

    # Entry Logic
    # If RSI crosses over lower_rsi, Open Buy Trade
    if crossesOver(iRSI, lower_rsi):
        print("   BUY SIGNAL!")
        print("   Opening Buy Trade...")
        enter("B", currency)
    # If RSI crosses under upper_rsi, Open Sell Trade
    if crossesUnder(iRSI, upper_rsi):
        print("   SELL SIGNAL!")
        print("   Opening Sell Trade...")
        enter("S", currency)

    # Exit Logic
    # If RSI is greater than upper_rsi and we have Buy Trade(s), Close Buy Trade(s)
    if iRSI[len(iRSI)-1] > upper_rsi and countOpenTrades("B", currency) > 0:
        print("   RSI above " + str(upper_rsi) + ". Closing Buy Trade(s)...")
        exit("B", currency)
    # If RSI is less than than lower_rsi and we have Sell Trade(s), Close Sell Trade(s)
    if iRSI[len(iRSI)-1] < lower_rsi and countOpenTrades("S", currency) > 0:
        print("   RSI below " + str(lower_rsi) + ". Closing Sell Trade(s)...")
        exit("S", currency)

    print(str(dt.datetime.now()) + "     " + timeframe + " Update Function Completed.\n")





