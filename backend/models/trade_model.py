from pydantic import BaseModel
class Tradeinput(BaseModel):
    stock:str
    action:str
    price:str
