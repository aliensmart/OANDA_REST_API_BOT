
import pandas as pd
import matplotlib.pyplot as plt
import time


class Ema_Macd:

    def EMA(self, df, f, s):
        """Function to calculate the EMAs"""
        df = df.copy()
        df['EMA_slow'] = df['Close'].ewm(span=s).mean()
        df['EMA_fast'] = df['Close'].ewm(span=f).mean()
        return df
        
    def ATR(self,df, n):
        "function to calculate True Range and Average True Range"
    #    DF = candles("EUR_USD")
        df = df.copy()
        df['H-L']=abs(df['High']-df['Low'])
        df['H-PC']=abs(df['High']-df['Close'].shift(1))
        df['L-PC']=abs(df['Low']-df['Close'].shift(1))
        df['TR']=df[['H-L','H-PC','L-PC']].max(axis=1,skipna=False)
        df['ATR'] = df['TR'].rolling(n).mean()
        #df['ATR'] = df['TR'].ewm(span=n,adjust=False,min_periods=n).mean()
        df2 = df.drop(['H-L','H-PC','L-PC'],axis=1)
        return round(df2["ATR"][-1], 4)


    def MACD(self, df ,a,b,c):
        """function to calculate MACD
        typical values a = 12; b =26, c =9"""
        df = df.copy()
        df["MA_Fast"]=df["Close"].ewm(span=a,min_periods=a).mean()
        df["MA_Slow"]=df["Close"].ewm(span=b,min_periods=b).mean()
        df["MACD"]=df["MA_Fast"]-df["MA_Slow"]
        df["Signal"]=df["MACD"].ewm(span=c,min_periods=c).mean()
        df.dropna(inplace=True)
        return df

    def trade_signal(self, df,  is_buy):
        "function to generate signal"
        signal = ""
        if is_buy == None:
            if df['EMA_fast'][-1] > df['EMA_slow'][-1] and  df['EMA_fast'][-2] > df['EMA_slow'][-2] and df["MACD"][-1] > df["Signal"][-1] and df["MACD"][-2] > df["Signal"][-2]:
                if df['EMA_fast'][-6] < df['EMA_slow'][-6]:
                    signal = "Buy"
            if df['EMA_fast'][-1] < df['EMA_slow'][-1] and  df['EMA_fast'][-2] < df['EMA_slow'][-2] and df["MACD"][-1] < df["Signal"][-1] and df["MACD"][-2] < df["Signal"][-2]:
                if df['EMA_fast'][-6] > df['EMA_slow'][-6]:
                    signal = "Sell"
                
        elif is_buy == True:
            if df['EMA_fast'][-1] < df['EMA_fast'][-1] or df["MACD"][-1] < df["Signal"][-1]:
                signal = "Close"
        elif is_buy == False:
            if df['EMA_fast'][-1] > df['EMA_fast'][-1] or df["MACD"][-1] > df["Signal"][-1]:
                signal = "Close"

        return signal