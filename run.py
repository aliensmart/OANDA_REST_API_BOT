import os
from Strategies.OANDA_MACD import MACD_RENKO
from Oanda_api.Oanda_api import Oanda_api
import time





pairs = ['EUR_USD','GBP_USD', 'AUD_USD', 'USD_JPY', 'EUR_JPY'] #currency pairs to be included in the strategy
#pairs = ['EUR_JPY','USD_JPY','AUD_JPY','AUD_USD','AUD_NZD','NZD_USD']
pos_size = 2000
token = os.environ.get("OANDA_DEMO_API")
account_id = "101-001-14058319-001"
api = Oanda_api(token, account_id)
macd_renko = MACD_RENKO()


def main():
    global pairs
# try:
    open_trades = api.get_trades()

    for i in range(len(open_trades)):    
        print("trading... ", open_trades[i]['instrument'])
    for currency in pairs:
        print("analyzing ",currency)
        is_buy = api.is_buy(currency)
        data = api.data(currency)
        ohlc  = data
        ohlc.columns = ["Open","High","Low","Close","Volume"]
        trade_signal = macd_renko.trade_signal(macd_renko.renko_merge(ohlc), is_buy)
        signal = trade_signal
        
        if signal == "Buy":
            api.buy(currency, (macd_renko.ATR2(ohlc, 14)), pos_size)
            print("New long position initiated for ", currency)
            
        elif signal == "Sell":
            api.sell(currency, (macd_renko.ATR2(ohlc, 14)), pos_size)
            print("New short position initiated for ", currency)
            
        elif signal == "Close":
            api.close(currency)
            print("closing all positon for ", currency)
                
        elif signal == "Close_Buy":
            api.close(currency)
            print("Existing Short position closed for ", currency)
            api.buy(currency, (macd_renko.ATR2(ohlc, 14)), pos_size)
            print("New long position initiated for ", currency)
            
        elif signal == "Close_Sell":
            api.close(currency)
            print("Existing long position closed for ", currency)
            api.sell(currency, (2*macd_renko.ATR2(ohlc, 14)), pos_size)
            print("New short position initiated for ", currency)
# except:
#     print("error encountered....skipping this iteration")


# Continuous execution        
starttime=time.time()
timeout = time.time() + 60*60*24*7  # 60 seconds times 60 meaning the script will run for 1 hr
while time.time() <= timeout:
    try:
        print("passthrough at ",time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        main()
        time.sleep(60 - ((time.time() - starttime) % 60.0)) # 1 minute interval between each new execution
    except KeyboardInterrupt:
        print('\n\nKeyboard exception received. Exiting.')
        exit()
