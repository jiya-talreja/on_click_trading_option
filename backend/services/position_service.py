import uuid

class PositionService:

    def create_position(self, trade_context):

        position_id = str(uuid.uuid4())

        position = {
            "position_id": position_id,
            "order_id": trade_context["order_id"],
            "stock": trade_context["stock"],
            "stock_id": trade_context["stock_id"],
            "action": trade_context["action"],
            "quantity": trade_context["quantity"],
            "entry_price": trade_context["filled_price"],
            "current_price": trade_context["filled_price"],
            "highest_price": trade_context["filled_price"],
            "lowest_price": trade_context["filled_price"],
            "stop_loss": trade_context["stoploss"],
            "trailing_stop": trade_context["stoploss"],
            "status": "ACTIVE",
            "entry_time": trade_context["order_time"],
            "exit_reason": None
        }

        return position
