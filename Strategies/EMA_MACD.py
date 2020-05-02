
import pandas as pd
import matplotlib.pyplot as plt
import time


class Ema_Macd:

    def __init__(self, df):
        self.df = df

    def EMA(self, f, s):
        """Function to calculate the EMAs"""
        df = self.df
        df['EMA_slow'] = df['c'].ewm(span=s).mean()
        df['EMA_fast'] = df['c'].ewm(span=f).mean()
        return df
        
    def ATR(self,n):
        "function to calculate True Range and Average True Range"
        df = self.df
        df['H-L']=abs(df['h']-df['l'])
        df['H-PC']=abs(df['h']-df['c'].shift(1))
        df['L-PC']=abs(df['l']-df['c'].shift(1))
        df['TR']=df[['H-L','H-PC','L-PC']].max(axis=1,skipna=False)
        df['ATR'] = df['TR'].rolling(n).mean()
        #df['ATR'] = df['TR'].ewm(span=n,adjust=False,min_periods=n).mean()
        df2 = df.drop(['H-L','H-PC','L-PC'],axis=1)
        return round(df2["ATR"][-1], 3)

    def MACD(self ,a,b,c):
        """function to calculate MACD
        typical values a = 12; b =26, c =9"""
        df = self.df
        df["MA_Fast"]=df["Close"].ewm(span=a,min_periods=a).mean()
        df["MA_Slow"]=df["Close"].ewm(span=b,min_periods=b).mean()
        df["MACD"]=df["MA_Fast"]-df["MA_Slow"]
        df["Signal"]=df["MACD"].ewm(span=c,min_periods=c).mean()
        df.dropna(inplace=True)
        return df

    def trade_signal(self, is_buy):
        "function to generate signal"
        signal = ""
        df = self.df
        if is_buy == None:
            if df['EMA_fast'][-1] > df['EMA_fast'][-1] and df["MACD"][-1] > df["Signal"][-1]:
                if df['EMA_fast'][-6] < df['EMA_fast'][-6]:
                    signal = "Buy"
            if df['EMA_fast'][-1] < df['EMA_fast'][-1] and df["MACD"][-1] < df["Signal"][-1]:
                if df['EMA_fast'][-6] > df['EMA_fast'][-6]:
                    signal = "Sell"
                
        elif is_buy == True or is_buy == False:
            if df['EMA_fast'][-1] == df['EMA_fast'][-1] or df["MACD"][-1] == df["Signal"][-1]:
                signal = "Close"

        return signal