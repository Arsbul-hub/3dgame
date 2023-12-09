import time
from requests import get
while True:
    old_time = time.time()
    d = get("http://5.230.84.38:2000/get_world").json()
    current_time = time.time()
    print(f"{current_time - old_time} секунд")
