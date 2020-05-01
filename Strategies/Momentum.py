from talib.abstract import *
import numpy as np

input_arrays = {
    'open': np.random.random(100),
    'high': np.random.random(100),
    'low': np.random.random(100),
    'close': np.random.random(100),
    'volume': np.random.random(100)
}

output1 = ADX(input_arrays, timeperiod=25) # calculate on close prices by default
output2 = SMA(input_arrays, timeperiod=25, price='open')
print(output1)
print(output2)

macd, macdsignal, macdhist = MACD(input_arrays['close'], fastperiod=12, slowperiod=26, signalperiod=9)