#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 06:23:40 2020

@author: alienmoore
"""

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

data = candles("EUR_USD")
data.to_csv("EUR_USD_15mn.csv",index=False)

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
    
    
def EMA(df, s, m, l):
    """Function to calculate the EMAs"""
    df['EMA_small'] = df['c'].ewm(span=s).mean()
    df['EMA_mid'] = df['c'].ewm(span=m).mean()
    df['EMA_long'] = df['c'].ewm(span=l).mean()
    return df

data = candles("EUR_USD")
rsi = rsi(data["c"], 14)
    
def ATR(DF,n):
    "function to calculate True Range and Average True Range"
    df = DF.copy()
    df['H-L']=abs(df['h']-df['l'])
    df['H-PC']=abs(df['h']-df['c'].shift(1))
    df['L-PC']=abs(df['l']-df['c'].shift(1))
    df['TR']=df[['H-L','H-PC','L-PC']].max(axis=1,skipna=False)
    df['ATR'] = df['TR'].rolling(n).mean()
    #df['ATR'] = df['TR'].ewm(span=n,adjust=False,min_periods=n).mean()
    df2 = df.drop(['H-L','H-PC','L-PC'],axis=1)
    return round(df2["ATR"][-1],2)

def trade_signal(df,curr, l_s):
    "function to generate signal"
    signal = ""

    if l_s["short"] == "0" and l_s["long"] == "0":
        if df["EMA_small"][-1] > df["EMA_mid"][-1] and df["EMA_small"][-2] > df["EMA_mid"][-2] and df["EMA_small"][-1] > df["EMA_long"][-1] and df["EMA_small"][-2] > df["EMA_long"][-2] and df["EMA_mid"][-1] > df["EMA_long"][-1] and df["EMA_small"][-5] < df["EMA_long"][-5]:
            signal = "Buy"
            
        elif df["EMA_small"][-1] < df["EMA_mid"][-1] and df["EMA_small"][-2] < df["EMA_mid"][-2] and df["EMA_small"][-1] < df["EMA_long"][-1] and df["EMA_small"][-2] < df["EMA_long"][-2] and df["EMA_mid"][-1] < df["EMA_long"][-1] and df["EMA_small"][-5] > df["EMA_long"][-5]:
            signal = "Sell"
    elif l_s["short"] != "0":    
        if df["EMA_small"][-1] > df["EMA_mid"][-1] and df["EMA_small"][-2] > df["EMA_mid"][-2] or df["EMA_small"][-1] > df["EMA_long"][-1] and df["EMA_small"][-2] > df["EMA_long"][-2]:
            signal = "Close"
    elif l_s["long"] != "0":    
        if df["EMA_small"][-1] < df["EMA_mid"][-1] and df["EMA_small"][-2] < df["EMA_mid"][-2] or df["EMA_small"][-1] < df["EMA_long"][-1] and df["EMA_small"][-2] < df["EMA_long"][-2]:
            signal = "Close"
            
    return signal

def main():
    global pairs
    try:
        r = trades.OpenTrades(accountID=account_id)
        open_trades = client.request(r)['trades']
        data_short = {
            "shortUnits": "ALL"}
        data_long = {
            "longUnits": "ALL"}
        
        for i in range(len(open_trades)):    
            print("trading... ", open_trades[i]['instrument'])
            
        for currency in pairs:
            print("analyzing ",currency)
            posit = positions.PositionDetails(accountID=account_id, instrument=currency)
            client.request(posit)
            open_pos = posit.response["position"]
            long_short = {}
            long_short["long"] = open_pos["long"]["units"]
            long_short["short"] = open_pos["short"]["units"]
            
            data = candles(currency)
            ohlc_df = EMA(data,5,10,50)
            
            signal = trade_signal(ohlc_df,currency, long_short)
            if signal == "Buy":
                market_order(currency,pos_size,0.1)
                print("New long position initiated for ", currency)
            elif signal == "Sell":
                market_order(currency,-1*pos_size,0.1)
                print("New short position initiated for ", currency)
            elif signal == "Close":
                if long_short["long"] !="0":
                    close_posit = positions.PositionClose(accountID=account_id, instrument=currency, data=data_long)
                    client.request(close_posit)
                    print("All long positions closed for ", currency)
                elif long_short["short"] !="0":
                    close_posit = positions.PositionClose(accountID=account_id, instrument=currency, data=data_short)
                    client.request(close_posit)
                    print("All short positions closed for ", currency)
                
    except:
        print("error encountered....skipping this iteration")


# Continuous execution        
starttime=time.time()
timeout = time.time() + (60*60*24)*4  # 60 seconds times 60 meaning the script will run for 24hr
while time.time() <= timeout:
    try:
        print("passthrough at ",time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        main()
        time.sleep(300 - ((time.time() - starttime) % 300.0)) # 5 minute interval between each new execution
    except KeyboardInterrupt:
        print('\n\nKeyboard exception received. Exiting.')
        exit()
        
        
    
