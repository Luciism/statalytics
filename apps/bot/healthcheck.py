import os
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

BOT_HEALTH_PORT = os.getenv("BOT_HEALTH_PORT")

try:
    with urlopen(f"http://bot:{BOT_HEALTH_PORT}/ready", timeout=3) as response:
        print(response.status, response.read().decode())

        if response.status == 200:
            exit(0)

except HTTPError as e:
    print("HTTP error:", e.code)
except URLError as e:
    print("Request failed:", e.reason)

exit(1)
