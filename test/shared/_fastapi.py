import asyncio
from datetime import datetime

from faker import Faker
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()


fake = Faker()

html_content = """
<html>
<body>
    <table>
        <head>
            <th>Name</th>
            <th>Age</th>
        </head>
        {}
    </table>
</body>
</html>
"""

rows = "\n".join(
    f"<tr><td>{fake.name()}</td><td>{fake.random_int(min=18, max=90)}</td></tr>"
    for _ in range(1000)
)

html = html_content.format(rows)


@app.get("/persons/{id}", response_class=HTMLResponse)
async def persons(id: int):
    return html


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
    await asyncio.sleep(seconds)
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
