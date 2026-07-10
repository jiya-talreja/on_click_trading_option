import uuid
from datetime import datetime
class OrderService:
    def mock_order(self,trade_context:dict):
        trade_context["order_id"]=str(uuid.uuid4())[:8]
        trade_context["order_time"] = datetime.now().isoformat()
        trade_context["order_status"]="PENDING"
        trade_context["filled_price"]=trade_context["cp"]
        trade_context["order_status"] = "FILLED"
        trade_context["broker_message"] = "Mock order executed successfully."
        return trade_context
    
