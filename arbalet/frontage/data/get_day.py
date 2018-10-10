import requests
import datetime
import time
import json


url = 'https://api.sunrise-sunset.org/json?lat=44.8404400&lng=-0.5805000&formatted=0'
outfile = 'sun/bordeaux.json'

now = datetime.datetime.now()
calendar = {}

try:
    for year in range(5):
        for i in range(0, 365):
            res = requests.get(url + '&date=' + now.isoformat())
            key = now.isoformat().split('T')[0]
            calendar[key] = res.json()['results']
            
            # Delete padding "+00:00"
            for field in calendar[key]:
                value = calendar[key][field]
                if isinstance(value, str) and "+" in calendar[key][field]:
                    calendar[key][field] = value.split('+')[0]

            print(key)

            now = now + datetime.timedelta(days=1)
            with open(outfile, 'w') as f: 
                json.dump(calendar, f, indent=4)
            time.sleep(0.005)
except KeyboardInterrupt:
    print("Loaded {} days into file {}".format(i+1, outfile))


