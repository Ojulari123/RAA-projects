#how to send GET request to a mock REST API
from urllib.request import urlopen
import ssl
import json

context = ssl._create_unverified_context() 

url = "https://jsonplaceholder.typicode.com/todos/1"

with urlopen(url, context=context) as response:
    body =  response.read()

mock_data = json.loads(body)
print(mock_data)