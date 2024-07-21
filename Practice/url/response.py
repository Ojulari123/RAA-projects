#this file just shows how to make a request to a sample domain
from urllib.request import urlopen
import ssl

#this is to handle any ssl vertification errors,because prior to using it I did get verification errors
context = ssl._create_unverified_context() 

with urlopen("https://www.example.com", context=context) as response:
    body = response.read()
print(body[:15])