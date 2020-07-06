import json
from urllib.request import urlopen
from datetime import datetime, timedelta

url = "https://c19downloads.azureedge.net/downloads/json/coronavirus-cases_latest.json"
source = json.loads(urlopen(url).read())

print("New data downloaded.")
print("Last data update: " + source['metadata']['lastUpdatedAt'])

# Subset
subset = ["Eastleigh","Test Valley","Winchester","Fareham","Southampton","Portsmouth"]
show_last = 15 # int(input("\nHow many days back? "))

# All days
sdate = datetime.strptime("2020-02-15", '%Y-%m-%d')
edate = datetime.strptime(source['metadata']['lastUpdatedAt'][0:10], '%Y-%m-%d')
span = edate - sdate
days = [(sdate + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(span.days + 1)]

# Table
data = {day:{area:-1 for area in subset} for day in days}

# Update with data
for x in source["ltlas"] + source["utlas"]:
    if x["areaName"] in subset:
        data[x["specimenDate"]][x["areaName"]] = x["totalLabConfirmedCases"]


#LOCF
locf = {area:0 for area in subset}

for day in days:
    for area in subset:
        if data[day][area] == -1:
            data[day][area] = locf[area]
        else:
            locf[area] = data[day][area]

print("\n\nDate".ljust(12), end='')
print(" ".join([i.center(11,' ') for i in subset]))

for i in [k for k in data.keys()][-show_last:]:
    print(i.ljust(10), end='')
    print(" ".join([str(data[i][j]).rjust(3).center(11,' ') for j in subset]))
