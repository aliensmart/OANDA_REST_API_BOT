import os
from Strategies.EMA_MACD import Ema_Macd
from Oanda_api.Oanda_api import Oanda_api
import time





pairs = ['EUR_USD','GBP_USD', 'AUD_USD', 'USD_JPY', 'EUR_JPY'] #currency pairs to be included in the strategy
#pairs = ['EUR_JPY','USD_JPY','AUD_JPY','AUD_USD','AUD_NZD','NZD_USD']
pos_size = 2000
token = os.environ.get("OANDA_DEMO_API")
account_id = "101-001-14058319-001"
api = Oanda_api(token, account_id)



def main():
    global pairs
    try:
        open_trades = api.get_trades()

        for i in range(len(open_trades)):    
            print("trading... ", open_trades[i]['instrument'])
        for currency in pairs:
            print("analyzing ",currency)
            is_buy = api.is_buy(currency)
            data = api.data(currency)
            ohlc  = data
            ohlc.columns = ["Open","High","Low","Close","Volume"]
            ema_macd = Ema_Macd()
            ohlc = ema_macd.EMA(ohlc, 8, 14)
            ohlc = ema_macd.MACD(ohlc, 12, 26, 9)
            trade_signal = ema_macd.trade_signal(ohlc, is_buy)
            signal = trade_signal
            
            if signal == "Buy":
                api.buy(currency, 2*(ema_macd.ATR(ohlc,14)), pos_size)
                print("New long position initiated for ", currency)
                
            elif signal == "Sell":
                api.sell(currency, 2*(ema_macd.ATR(ohlc,14)), pos_size)
                print("New short position initiated for ", currency)
            elif signal == "Close":
                api.close(currency)
    except:
        print("error encountered....skipping this iteration")


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
