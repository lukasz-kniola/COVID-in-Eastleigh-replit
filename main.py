import json
import requests
from datetime import datetime, timedelta

# Subset
subset = [
    "Eastleigh", "Test Valley", "Winchester", 
    "Southampton", "Fareham", "Gosport", "Portsmouth",
]

def read_in_area(area):
  url = "https://api.coronavirus-staging.data.gov.uk/v1/data?"

  params = {"filters": "areaName="+area,
            "structure": '{"areaName":"areaName","date":"date","newCases":"newCasesBySpecimenDate","cumCases":"cumCasesBySpecimenDate"}',
            "format": "json",
            "page": 1}

  request = requests.get(url, params=params)
  data = request.json()['data']

  print(area + " data downloaded.")
  return data

# Subset
subset = [
    "Eastleigh", "Test Valley", "Winchester", 
    "Southampton", "Fareham", "Gosport", "Portsmouth",
]

source = []
for area in subset:
    source += read_in_area(area)



# All days
fst_record = datetime.strptime("2020-01-01", '%Y-%m-%d')
lst_record = max([datetime.strptime(x["date"], '%Y-%m-%d') for x in source])
span = lst_record - fst_record
days = [(fst_record + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(span.days + 1)]

print("Last updated: "+str(lst_record)[0:10])

# All areas
areas = set(subset)

# Table
data = {day: {area: -1 for area in areas} for day in days}

# Update with data
for x in source:
	data[x["date"]][x["areaName"]] = x["cumCases"]

#LOCF
locf = {area: 0 for area in areas}

for day in days:
	for area in areas:
		if data[day][area] == -1:
			data[day][area] = locf[area]
		else:
			locf[area] = data[day][area]


def offset(dtc, offset):
	return (datetime.strptime(dtc, '%Y-%m-%d') +
	        timedelta(days=offset)).isoformat()[:10]


def report(days):
	print("\n\nDate".ljust(13), end='')
	print(" ".join([i.center(11, ' ') for i in subset]))

	for _date in list(data.keys())[-days:]:
		print(_date.ljust(11), end='')
		for j in subset:
			_cases = data[_date][j]

			_cases_1 = data[offset(_date, -1)][j]
			_cases_8 = data[offset(_date, -8)][j]
			_diff1 = _cases - _cases_1
			_diff8 = _cases - _cases_8

			if _diff8 == 0:
				_tx = "\33[94m" + str(_cases) + "\033[0m"
			elif _diff8 <= 2:
				_tx = "\33[92m" + str(_cases) + "\033[0m"
			elif _diff8 <= 5:
				_tx = "\33[93m" + str(_cases) + "\033[0m"
			elif _diff8 <= 9:
				_tx = "\33[33m" + str(_cases) + "\033[0m"
			else:
				_tx = "\33[91m" + str(_cases) + "\033[0m"

			if _diff1 <= 4:
				_inc = "+" * _diff1 + " " * (4 - _diff1)
			else:
				_inc = "+++>"

			print(_tx.rjust(16) + _inc, end=' ')

		print()


report(15)
while True:
	show_days = input("\nHow many days back? ")
	if show_days == "":
		break
	report(int(show_days))
