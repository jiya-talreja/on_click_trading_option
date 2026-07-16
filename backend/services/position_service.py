import uuid
from services.stoploss import StopLossDync
class PositionService:
    def create_position(self, trade_context):
        stoploss_service = StopLossDync()
        entry_price = trade_context["filled_price"]
        stop_loss = stoploss_service.stoploss(
            trade_context["action"],
            entry_price,
            1
        )
        trailing_stop = stoploss_service.initialtsl(
            trade_context["action"],
            entry_price,
            1
        )
        position_id = str(uuid.uuid4())[:8]
        position = {
            "position_id": position_id,
            "order_id": trade_context["order_id"],
            "stock": trade_context["stock"],
            "stock_id": trade_context["stock_id"],
            "action": trade_context["action"],
            "quantity": trade_context["quantity"],
            "entry_price": entry_price,
            "current_price": entry_price,
            "highest_price": entry_price,
            "lowest_price": entry_price,
            "stop_loss": stop_loss,
            "trailing_stop": trailing_stop,
            "status": "ACTIVE",
            "entry_time": trade_context["order_time"],
            "exit_reason": None
        }
        return position
