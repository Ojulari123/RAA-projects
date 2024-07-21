# #prints out a list of attributes and methods available in response
# from urllib.request import urlopen
# import ssl
# from pprint import pprint

# context = ssl._create_unverified_context() 

# with urlopen("https://www.example.com", context=context) as response:
#     pprint(dir(response))


#prints out the headers and the items available in response
from urllib.request import urlopen
import ssl
from pprint import pprint

context = ssl._create_unverified_context() 

with urlopen("https://www.example.com", context=context) as response:
    pass
pprint(response.headers.items())
pprint(response.getheader("server")) #same with .header("server")
response.close()


