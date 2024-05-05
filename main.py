from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
app.last_msg = None


class TradeRequest(BaseModel):
    msg: str


@app.get("/")
def read_root():
    return app.last_msg
    # return {"Hello": "World"}


@app.post("/trade")
def trade(request: TradeRequest):
    app.last_msg = request
    return "ok"


# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}