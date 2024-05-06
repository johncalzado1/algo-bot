from typing import Union
from pprint import pprint
from fastapi import FastAPI
from pydantic import BaseModel
import time, hashlib, time, hmac, base64, requests, json, os

app = FastAPI()
app.last_msg = None


app.api_key = os.getenv("KC_API_KEY", None)
app.api_secret = os.getenv("KC_API_SECRET", None)
app.api_passphrase = os.getenv("KC_API_PASS", None)
# app.base_url = "https://api.kucoin.com/api/v1/orders"  # spot
app.base_url = 'https://api-futures.kucoin.com' # futures 
# app.base_url = 'https://api-futures.kucoin.com/api/v1/position?symbol=XBTUSDM'


class TradeRequest(BaseModel):
    msg: str
    price: str
    size_usdt: str
    action: str # long, short, close


def get_time():
    return int(time.time() * 1000)

def get_headers(_str_to_sign):
    signature = base64.b64encode(
        hmac.new(app.api_secret.encode('utf-8'), _str_to_sign.encode('utf-8'), hashlib.sha256).digest())
    passphrase = base64.b64encode(hmac.new(app.api_secret.encode('utf-8'), app.api_passphrase.encode('utf-8'), hashlib.sha256).digest())
    return {
        'Content-type':'application/json', 
        'Accept':'application/json',
        "KC-API-SIGN": signature,
        "KC-API-TIMESTAMP": str(get_time()),
        "KC-API-KEY": app.api_key,
        "KC-API-PASSPHRASE": passphrase,
        "KC-API-KEY-VERSION": "2"
    }


def trade(side, size_usdt, stopType=None, stopPrice=None, stopPriceType="TP", type="market"):
    """Opens a position
    side (str): "buy" or "sell"
    size_usdt (int): 
    type (str): "market" or "limit"
    stopType (str): up (for shorts) OR down (for longs)
    """
    
    data = { # futures
        "clientOid": "jc-trade",
        "side": side,
        "symbol": "XBTUSDTM", 
        "leverage": "125", 
        "type": "market", 
        "size": size_usdt,
    } 

    if "stop" != None:
        data.update({
            "stop": stopType,
            "stopPrice": stopPrice,
            "stopPriceType": stopPriceType
        })

    data_json = json.dumps(data)
    
    url = app.base_url + '/api/v1/orders'
    str_to_sign = str(get_time()) + 'POST' + "/api/v1/orders" + data_json

    headers = get_headers(str_to_sign)

    response = requests.request("post", url=url, headers=headers, data=data_json)
    print(response.status_code)
    print(response.json())



def close_all_pos():
    """Close all trades
    """
    data = {
        "clientOid": "jc-trade",
        "symbol": "XBTUSDTM", 
        "type": "market",
        "closeOrder": True
    }

    data_json = json.dumps(data)
    
    url = app.base_url + '/api/v1/orders'
    str_to_sign = str(get_time()) + 'POST' + '/api/v1/orders' + data_json

    headers = get_headers(str_to_sign)

    response = requests.request("post", url=url, headers=headers, data=data_json)
    print(response.status_code)
    print(response.json())


@app.get("/")
def read_root():
    return app.last_msg
    # return {"Hello": "World"}

@app.get("/close")
def closeTrades():
    close_all_pos()

@app.post("/action")
def action(request: TradeRequest):
    action = request.action

    if action == "long":
        trade(side="buy", size_usdt=request.size_usdt)
        print("LONG - {0} - {1}".format(request.msg, request.price))
    elif action == "short":
        trade(side="sell", size_usdt=request.size_usdt)
        print("SHORT - {0} - {1}".format(request.msg, request.price))
    elif action == "close":
        close_all_pos()
        print("CLOSE position (SL/TP) - {0}".format(request.price))
    else:
        return "Invalid action: {0}".format(request)
    
    pprint(request.model_dump_json())
    return "ok"


# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}