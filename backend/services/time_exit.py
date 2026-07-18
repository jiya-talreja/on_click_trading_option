from datetime import datetime
def market_closed():
    now=datetime.now()
    return (now.hour>15 or (now.hour==15 and now.minute>=28))
