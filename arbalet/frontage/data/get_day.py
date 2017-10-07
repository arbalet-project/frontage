import requests
import datetime
import time
import json


url = 'https://api.sunrise-sunset.org/json?lat=44.8404400&lng=-0.5805000&formatted=0'

with open('bordeaux.sun', 'w') as outfile:

    d = datetime.datetime.now()
    t = {}
    for i in range(0, 365):
        res = requests.get(url+'&date='+d.isoformat())
        t[d.isoformat()] = res.json()['results']
        print(res.json())
        d = d + datetime.timedelta(days=1)
        time.sleep(0.005)

    print('---------------------')
    print(t)
    outfile.write(json.dumps(t))


