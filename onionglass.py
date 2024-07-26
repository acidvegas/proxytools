import urllib.request
import json

https://metrics.torproject.org/onionoo.html#details

response = urllib.request.urlopen('https://onionoo.torproject.org/details')
data = json.loads(response.read())


for item in data['relays']:
    print(item)

for item in data['bridges']:
    print(item)