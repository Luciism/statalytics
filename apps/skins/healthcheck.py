import os
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

SKINS_PORT = os.getenv("SKINS_PORT")

try:
    with urlopen(f"http://skins:{SKINS_PORT}/", timeout=3) as response:
        print(response.status, response.read().decode())

        if response.status == 200:
            exit(0)

except HTTPError as e:
    print("HTTP error:", e.code)
except URLError as e:
    print("Request failed:", e.reason)

exit(1)
