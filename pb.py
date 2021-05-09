import requests
import json
import re
URL = "https://belarusbank.by/api/kursExchange"
def load_exchange():
    return json.loads(requests.get(URL).text)
def get_exchange(gorod):
    for exc in load_exchange():
        if gorod == exc['name']:
            return exc
    return False
