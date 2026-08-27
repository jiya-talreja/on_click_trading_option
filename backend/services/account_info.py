from core.config import settings
import requests
from dhanhq import dhanhq
from dhanhq import DhanContext
class AccountService:
    def __init__(self):
        self.client_id = settings.client_key
        self.access_token = settings.access_token
        self.headers = {
            "client-id": self.client_id,
            "access-token": self.access_token
        }
        context = DhanContext(settings.client_key,self.access_token)
        self.dhan = dhanhq(context)
        print("DHAN : ",self.dhan)
        print("Account Service Initialized")
    def get_funds(self):
        print("Calling Dhan Funds API")
        response=self.dhan.get_fund_limits()
        print(response)
        return response
        

        
