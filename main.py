from typing import Union

from fastapi import FastAPI

app = FastAPI()


last_msg = ""

@app.get("/")
def read_root():
    return last_msg
    # return {"Hello": "World"}


@app.post("/trade")
def trade(request):
    last_msg = request


# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}