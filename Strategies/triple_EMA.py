#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 06:23:40 2020

@author: alienmoore
"""
import pandas as pd
import matplotlib.pyplot as plt
import time
import os
from pyti.relative_strength_index import relative_strength_index as rsi
    
    
def EMA(df, s, m, l):
    """Function to calculate the EMAs"""
    df['EMA_small'] = df['c'].ewm(span=s).mean()
    df['EMA_mid'] = df['c'].ewm(span=m).mean()
    df['EMA_long'] = df['c'].ewm(span=l).mean()
    return df
    
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

