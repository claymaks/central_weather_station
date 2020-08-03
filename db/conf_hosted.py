import csv
import requests
import dateutil.parser
import datetime


addr = "https://cmaks-weather.herokuapp.com/add-data/"

with open("weather.csv","r") as my_csv:
        for row in csv.reader(my_csv):
            dt = ((dateutil.parser.parse(row[0]) - datetime.datetime(1970, 1, 1)).total_seconds())
            requests.put(addr + "TEMPERATURE", json={'dt': int(dt),
                                                     'inside': float(row[1]),
                                                     'outside': float(row[2])})
            requests.put(addr + "HUMIDITY", json={'dt': int(dt),
                                                     'inside': float(row[4]),
                                                     'outside': float(row[5])})
            print(dt)
