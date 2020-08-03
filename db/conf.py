import csv
import datetime
import dateutil.parser
from api import insert_data

with open("weather.csv","r") as my_csv:
        for row in csv.reader(my_csv):
            dt = ((dateutil.parser.parse(row[0]) - datetime.datetime(1970, 1, 1)).total_seconds())
            #print(int(dt))
            insert_data("TEMPERATURE", int(dt), float(row[1]), float(row[2]))
            insert_data("HUMIDITY", int(dt), float(row[4]), float(row[5]))
