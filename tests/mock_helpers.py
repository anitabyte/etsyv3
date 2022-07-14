class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


def mocked_requests_get(*args, **kwargs):
    uri = args[0]
    if "users/UNAUTHORIZED" in uri:
        return MockResponse(None, 401)
    return MockResponse(None, 200)
