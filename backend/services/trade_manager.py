from services.quantity_info import QuantityInfo
from services.stoploss import StopLossDync
from services.validation import ValidationService
from services.order_service import OrderService
from services.position_service import PositionService
from services.account_info import AccountService
from storage.redis_storage import save_position,get_position,update_position,delete_position,get_all_position
CAPITAL_PERCENTAGE=90
class Trade_manager:
    def business_logic(self,trade_context):
        
        account_service = AccountService()    
        funds=account_service.get_funds() 
        avail_amount=funds["data"]["availabelBalance"]  
        trade_context["balance"]=avail_amount
        print("FUNDS : ",funds)

        quantity_service=QuantityInfo()
        quantity=quantity_service.calculate_quantity(avail_amount,trade_context["cp"],CAPITAL_PERCENTAGE)
        print(quantity)
        trade_context["quantity"]=quantity
        
        validate_service=ValidationService()
        if_true=validate_service.validate(trade_context)
        print(if_true)
        if(if_true):
            order_service=OrderService()
            trade_context=order_service.mock_order(trade_context)
            print("update trade_context")
            print(trade_context)
        if(trade_context["order_status"]=="FILLED"):
            print("a")
            position_service=PositionService()
            position=position_service.create_position(trade_context)
            print("psotion created : ",position)
            save_position(position)
            saved_position = get_position(position["position_id"])
            print(saved_position)
            trade_context["position_id"] = position["position_id"]
        return trade_context
