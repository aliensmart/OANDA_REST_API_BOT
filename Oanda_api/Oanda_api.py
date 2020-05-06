#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.trades as trades
import oandapyV20.endpoints.positions as positions
import pandas as pd


class Oanda_api:

    def __init__(self, token, account_id):
        self.token = token
        self.client = oandapyV20.API(access_token=self.token,environment="practice")
        self.id = account_id


    def data(self, instrument):
        params = {"count": 800,"granularity": "M15"} #granularity can be in seconds S5 - S30, minutes M1 - M30, hours H1 - H12, days D, weeks W or months M
        candles = instruments.InstrumentsCandles(instrument=instrument,params=params)
        self.client.request(candles)
        ohlc_dict = candles.response["candles"]
        ohlc = pd.DataFrame(ohlc_dict)
        ohlc_df = ohlc.mid.dropna().apply(pd.Series)
        ohlc_df["volume"] = ohlc["volume"]
        ohlc_df.index = ohlc["time"]
        ohlc_df = ohlc_df.apply(pd.to_numeric)
        return ohlc_df

    def market_order(self, instrument,units,sl):
        """units can be positive or negative, stop loss (in pips) added/subtracted to price """  
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
        r = orders.OrderCreate(accountID=self.id, data=data)
        self.client.request(r)

    def buy(self, instrument, sl, pos):
        self.market_order(instrument,pos, sl)

    def sell(self, instrument, sl, pos):
        self.market_order(instrument,-1*pos, sl)

    def is_buy(self, instrument):
        all_positions = positions.PositionDetails(accountID=self.id, instrument=instrument)
        self.client.request(all_positions)
        open_pos = all_positions.response["position"]
        long_short = {}
        long_short["long"] = open_pos["long"]["units"]
        long_short["short"] = open_pos["short"]["units"]

        if long_short["long"]!="0" and long_short["short"]=="0":
            return True
        if long_short["short"]!="0" and long_short["long"]=="0":
            return False
        return None
    
    def close(self, instrument):
        data_short = {
        "shortUnits": "ALL"}
        data_long = {
            "longUnits": "ALL"}
        if self.is_buy(instrument)==True:
            close_posit = positions.PositionClose(accountID=self.id, instrument=instrument, data=data_long)
            self.client.request(close_posit)
            print("Closing all long positions ", instrument)
        if self.is_buy(instrument)==False:
            close_posit = positions.PositionClose(accountID=self.id, instrument=instrument, data=data_short)
            self.client.request(close_posit)
            print("Closing all Short positions ", instrument)

    
    def get_trades(self):
        r = trades.OpenTrades(accountID=self.id)
        open_trades = self.client.request(r)['trades']
        return open_trades




    

