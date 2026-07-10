class ValidationService:

    def validate(
        self,
        trade_context:dict
    ):
        if not trade_context["stock"]:
            raise ValueError("Stock is missing.")
        if trade_context["action"] not in ["BUY", "SELL"]:
            raise ValueError("Invalid Action.")
        if trade_context["balance"] <= 0:
            raise ValueError("No balance available.")
        if trade_context["cp"] <= 0:
            raise ValueError("Invalid current price.")
        if trade_context["quantity"] <= 0:
            raise ValueError("Quantity must be greater than zero.")
        if trade_context["action"] == "BUY":
            if trade_context["stoploss"] >= trade_context["cp"]:
                raise ValueError(
                    "BUY stop loss must be below current price."
                )
            #if trailing_stop >= trade_context["cp"]:
             #   raise ValueError(
              #      "BUY trailing stop must be below current price."
               # )
        elif trade_context["action"] == "SELL":
            if trade_context["stoploss"] <= trade_context["cp"]:
                raise ValueError(
                    "SELL stop loss must be above current price."
                )
            #if trailing_stop <= current_price:
             #   raise ValueError(
              #      "SELL trailing stop must be above current price."
               # )
        return True
