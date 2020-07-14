import json
from urllib.request import urlopen
from datetime import datetime, timedelta

url = "https://c19downloads.azureedge.net/downloads/json/coronavirus-cases_latest.json"
source = json.loads(urlopen(url).read())

print("New data downloaded.")
print("Last data update: " + source['metadata']['lastUpdatedAt'])

# Subset
subset = ["Eastleigh","Test Valley","Winchester","Fareham","Southampton","Portsmouth"]

# All days
sdate = datetime.strptime("2020-01-01", '%Y-%m-%d')
edate = datetime.strptime(source['metadata']['lastUpdatedAt'][0:10], '%Y-%m-%d')
span = edate - sdate
days = [(sdate + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(span.days + 1)]

# All areas
areas = set([x["areaName"] for x in source["ltlas"] + source["utlas"]])

# Table
data = {day:{area:-1 for area in areas} for day in days}

# Update with data
for x in source["ltlas"] + source["utlas"]:
    data[x["specimenDate"]][x["areaName"]] = x["totalLabConfirmedCases"]

#LOCF
locf = {area:0 for area in areas}

for day in days:
    for area in areas:
        if data[day][area] == -1:
            data[day][area] = locf[area]
        else:
            locf[area] = data[day][area]

def offset(dtc, offset):
    return (datetime.strptime(dtc, '%Y-%m-%d') + timedelta(days=offset)).isoformat()[:10]

def report(days):
    print("\n\nDate".ljust(13), end='')
    print(" ".join([i.center(11,' ') for i in subset]))

    for _date in list(data.keys())[-days:]:
        print(_date.ljust(11), end='')
        for j in subset:
            _cases = data[_date][j]

            _cases_1 = data[offset(_date,-1)][j]
            _cases_10 = data[offset(_date,-10)][j]
            _diff1 = _cases - _cases_1
            _diff10 = _cases - _cases_10

            if _diff10 == 0:
                _tx = "\33[94m"+str(_cases)+"\033[0m"
            elif _diff10 <=1:
                _tx = "\33[92m"+str(_cases)+"\033[0m"
            elif _diff10 <=4:
                _tx = "\33[93m"+str(_cases)+"\033[0m"
            elif _diff10 <=9:
                _tx = "\33[33m"+str(_cases)+"\033[0m"
            else:
                _tx = "\33[91m"+str(_cases)+"\033[0m"

            if _diff1 <= 4:
                _inc = "+"*_diff1 + " "*(4-_diff1)
            else:
                _inc = "+++>"

            print(_tx.rjust(16) + _inc, end=' ')

        print()

report(15)
while True:
    show_days = input("\nHow many days back? ")
    if show_days == "":
        new_area = input("Any other area? ")
        if new_area == "":
            break
        elif new_area in areas:
            subset = [new_area,] + subset[0:-1]
            show_days = 15
        else:
            print("\n" + new_area + " not recognized.")
            show_days = 15
    report(int(show_days))
