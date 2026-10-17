import os
from urllib.error import HTTPError, URLError
from urllib.request import urlopen, Request

HEALTH_API_KEY = os.getenv("HEALTH_API_KEY")
assert HEALTH_API_KEY, "HEALTH_API_KEY is not set"

try:
    request = Request(
        "http://health:8000/ready",
        headers={"X-Api-Key": HEALTH_API_KEY},
    )
    with urlopen(request, timeout=3) as response:
        print(response.status, response.read().decode())

        if response.status == 200:
            exit(0)

except HTTPError as e:
    print("HTTP error:", e.code)
except URLError as e:
    print("Request failed:", e.reason)

exit(1)
