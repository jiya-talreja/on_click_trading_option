import math
class StopLossDync:
    def stoploss(
            self,
            action:str,
            current_price:float,
            stop_percent:float
    ):
        inter=current_price*(stop_percent/100)
        if action=="BUY":
            return round(current_price-inter,2)
        elif action == "SELL":
            return round(current_price + inter, 2)
        else:
            raise ValueError("Action must be BUY or SELL") 
    def initialtsl(
            self,
            action:str,
            current_price:float,
            stop_percent:float
    ):
        return self.stoploss(action,
            current_price,
            stop_percent)
    def update_trailing_stop(
        self,
        action: str,
        current_price: float,
        highest_price: float,
        lowest_price: float,
        trailing_percent: float
    ):
        if action == "BUY":
            if current_price > highest_price:
                highest_price = current_price
            tsl = highest_price * (1 - trailing_percent / 100)
            return round(tsl,2), highest_price
        elif action=="SELL":
            if current_price < lowest_price:
                lowest_price=current_price
            tsl=lowest_price*(1+trailing_percent/100)
            return round(tsl,2),lowest_price
        else:
            raise ValueError("Action must be BUY or SELL")
    def exit_check(
        self,
        action: str,
        current_price: float,
        trailing_stop: float
    ):
        action = action.upper()
        if action == "BUY":
            return current_price <= trailing_stop
        elif action == "SELL":
            return current_price >= trailing_stop
        else:
            raise ValueError("Action must be BUY or SELL")
