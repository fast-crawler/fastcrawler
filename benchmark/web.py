from faker import Faker
from fastapi import FastAPI
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


@app.get("/{id}", response_class=HTMLResponse)
async def root(id: int):
    return html


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
