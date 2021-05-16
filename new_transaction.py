import requests
import json

headers = {'Content-Type': 'application/json; charset=utf-8'}
data = {
    "sender": "jjaginggoo",
    "recipient": "jjagingoo2",
    "amount": "33"
}
print(requests.post("http://localhost:5000/transactions/new", headers=headers, data=json.dumps(data)).content)