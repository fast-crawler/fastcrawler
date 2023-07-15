import asyncio
import logging
import random
import string
from datetime import datetime

from fastapi import FastAPI, Request

try:
    from colorama import Fore
except Exception:

    class Fore:
        pass


COLORED = True if hasattr(Fore, "RED") else False
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger.addHandler(handler)


app = FastAPI()


def get_random_id():
    return "".join(random.choices(string.ascii_lowercase, k=5))


@app.get("/cookies/")
async def cookies(request: Request):
    print(request.cookies)
    return request.cookies


@app.get("/headers/")
async def headers(request: Request):
    print(request.headers)
    return request.headers


@app.get("/throtlled/{seconds}/")
async def throtlled(request: Request, seconds: int):
    req_id = get_random_id()
    start = Fore.RED if COLORED else ""
    reset = Fore.RESET if COLORED else ""
    end = Fore.BLUE if COLORED else ""
    logger.info(f"throtlled request for {seconds}(sec) :: {start}{req_id = }{reset}")
    await asyncio.sleep(seconds)
    logger.info(f"throtlled request finished :: {end}{req_id = }{reset}")
    return {
        "response": "OK",
    }


@app.get("/")
async def root():
    return {"time": str(datetime.now())}


@app.get("/get")
def get():
    return "Hello, from test_server!"


@app.post("/post")
def post(data: dict | str):
    return data


@app.put("/put")
def put(data: dict | str):
    return data


@app.delete("/delete")
def delete():
    return "Deleted!"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
