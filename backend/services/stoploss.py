import pandas as pd
class StopLossDync:
    def stoploss(
        self,
        action: str,
        price: float,
        atr_component: float
    ):
        multiplier=1
        atr_buffer = atr_component*multiplier
        if action == "BUY":
            return round(price - atr_buffer,2)
        elif action == "SELL":
            return round(price + atr_buffer,2)
        else:
            raise ValueError("Action must be BUY or SELL")
    def initialtsl(
        self,
        action: str,
        price: float,
        atr_component: float
    ):
        return self.stoploss(
            action,
            price,
            atr_component
        )
    def update_trailing_stop(
        self,
        action: str,
        current_price: float,
        highest_price: float,
        lowest_price: float,
        atr_component: float
    ):
        action = action.upper()
        multiplier=1
        atr_buffer = atr_component*multiplier
        if action == "BUY":
            if current_price > highest_price:
                highest_price = current_price
            tsl = highest_price - atr_buffer
            return round(tsl, 2), highest_price
        elif action == "SELL":
            if current_price < lowest_price:
                lowest_price = current_price
            tsl = lowest_price + atr_buffer
            return round(tsl, 2), lowest_price
        else:
            raise ValueError("Action must be BUY or SELL")
    def exit_check_tsl(
        self,
        action: str,
        current_price: float,
        trailing_stop: float
    ):
        action = action.upper()
        if action == "BUY":
            return {
            "exit": current_price <= trailing_stop,
            "reason": "TRAILING_STOP"
            }
        elif action == "SELL":
            return {
            "exit": current_price >= trailing_stop,
            "reason": "TRAILING_STOP"
            }
        else:
            raise ValueError("Action must be BUY or SELL")
    def calculate_atr_from_candles(self,raw_candles,mean_period=14):
        print("inside function")
        if not raw_candles or len(raw_candles)<=mean_period:
            print("candle return issue")
            return None
        print(raw_candles)
        df=pd.DataFrame(raw_candles,columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'oi'])
        #reveersing from past to present 
        df=df.iloc[::-1].reset_index(drop=True)
        print("reverse")
        df['high']=df['high'].astype(float)
        df['low']=df['low'].astype(float)
        df['close']=df['close'].astype(float)

        df['h_m_l']=df['high']-df['low']
        df['h_m_c']=(df['high']-df['close'].shift(1)).abs()#look at one above for close(previous close)
        df['l_m_c']=(df['low']-df['close'].shift(1)).abs()

        df['tr']=df[['h_m_l','h_m_c','l_m_c']].max(axis=1)#select 3 cols do row wise max
        df['atr']=df['tr'].ewm(alpha=1 / mean_period, adjust=False).mean()
        latest_atr=round(df['atr'].iloc[-1],2)
        print(latest_atr)
        return latest_atr
