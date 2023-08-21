from fastcrawler.engine import AioHttpEngine


class TestServer:
    def __init__(self):
        self.responses = {
            "GET": {"message": "GET request received"},
            "POST": {"message": "POST request received"},
            "PUT": {"message": "PUT request received"},
            "DELETE": {"message": "DELETE request received"},
        }

    def get_response(self, method, data=None):
        response = self.responses.get(method)
        if data:
            response["data"] = data
        return response


class TestClient(AioHttpEngine):
    def __init__(self, server=TestServer(), headers=None, proxy=None):
        self.server = server

    def get(self, url):
        response = self.server.get_response("GET")
        return response

    def post(self, url, data):
        response = self.server.get_response("POST", data=data)
        return response

    def delete(self, url):
        response = self.server.get_response("DELETE")
        return response

    def put(self, url, data):
        response = self.server.get_response("PUT", data=data)
        return response


# prepare test

server = TestServer()
client = TestClient(server)

# Test GET method
response = client.get("http://example.com")
assert response == {"message": "GET request received"}

# Test POST method
data = {"key": "value"}
response = client.post("http://example.com", data=data)
assert response == {"message": "POST request received", "data": {"key": "value"}}

# Test DELETE method
response = client.delete("http://example.com")
assert response == {"message": "DELETE request received"}

# Test PUT method
data = {"key": "new_value"}
response = client.put("http://example.com", data=data)
assert response == {"message": "PUT request received", "data": {"key": "new_value"}}
