import math
class QuantityInfo:
    def calculate_quantity(
        self,
        available_balance: float,
        current_price: float,
        capital_percentage: float
    ):
        capital_to_use=available_balance*(capital_percentage/100)
        quantity=math.floor(capital_to_use / current_price)
        return quantity
