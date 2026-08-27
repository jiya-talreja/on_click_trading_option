import time
import json
import traceback
from services.account_info import AccountService
account = AccountService()
class OrderService:
    def __init__(self):
        self.dhan = account.dhan
    def place_order(self, trade_context):
        print("DHAN ALL : ",self.dhan)
        transaction = (
            self.dhan.BUY
            if trade_context["action"] == "BUY"
            else self.dhan.SELL
        )
        try:
            print("\n========== PLACING ORDER ==========")
            print("Security ID :", trade_context["stock_id"])
            print("Transaction :", transaction)
            print("Quantity    :", trade_context["quantity"])
            print(self.dhan.MARKET)
            print(self.dhan.LIMIT)
            print(self.dhan.INTRA)
            print(self.dhan.DAY)
            response = self.dhan.place_order(
                security_id=str(trade_context["stock_id"]),
                exchange_segment=self.dhan.NSE,
                transaction_type=transaction,
                quantity=int(trade_context["quantity"]),
                order_type=self.dhan.MARKET,
                product_type=self.dhan.INTRA,
                price=0,
                trigger_price=0,
                validity=self.dhan.DAY,
                after_market_order=False,
                amo_time="OPEN"
            )
            print("\nPLACE ORDER RESPONSE")
        except Exception:
            traceback.print_exc()
            trade_context["order_status"] = "FAILED"
            trade_context["broker_message"] = "Broker Exception"
            return trade_context
        if response.get("status") != "success":
            trade_context["order_status"] = "FAILED"
            trade_context["broker_message"] = response["remarks"]["error_message"]
            return trade_context
        order_id = response["data"]["orderId"]
        trade_context["order_id"] = order_id
        print("\nOrder Accepted")
        print("Order ID :", order_id)
        while True:
            try:
                order = self.dhan.get_order_by_id(order_id)
                print("\nORDER LOOKUP")
                print(json.dumps(order, indent=4))
            except Exception:
                traceback.print_exc()
                trade_context["order_status"] = "FAILED"
                trade_context["broker_message"] = "Unable to fetch order status"
                return trade_context
            if order.get("status") != "success":
                print("Order lookup unsuccessful. Retrying...")
                time.sleep(1)
                continue
            order_data = order["data"][0]
            broker_status = order_data["orderStatus"]
            print("Current Broker Status :", broker_status)
            if broker_status in [
                "TRANSIT",
                "PENDING",
                "TRIGGERED",
                "PART_TRADED"
            ]:
                print("Waiting for final execution...")
                time.sleep(1)
                continue
            if broker_status == "TRADED":
                print("ORDER FILLED")
                trade_context["order_status"] = "FILLED"
                trade_context["filled_price"] = (
                    order_data.get("averageTradedPrice")
                    or order_data.get("price")
                )
                trade_context["order_time"] = (
                    order_data.get("exchangeTime")
                    or order_data.get("updateTime")
                )
                trade_context["broker_message"] = "Order Filled Successfully"
                return trade_context
            if broker_status in [
                "REJECTED",
                "CANCELLED",
                "EXPIRED",
                "INACTIVE"
            ]:
                print("ORDER FAILED")
                trade_context["order_status"] = "FAILED"
                trade_context["broker_message"] = broker_status
                return trade_context
