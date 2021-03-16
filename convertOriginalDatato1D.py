# -*- coding: shift-jis -*-
import datetime as dt
import pandas as pd
import numpy as np
import os
import sys

daysJP = ["日曜日", "月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日"]
daysEN = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

originalFolder = ".\\data\\original"
filelist = [f for f in os.listdir(originalFolder) if os.path.isfile(os.path.join(originalFolder, f))]
placeValues = []
placeNames= []
for l in range(len(filelist)):
    file = filelist[l]
    df = pd.read_csv(originalFolder + "\\" + file)
    values = []
    indexValues = []
    j = daysJP.index(df.values[0][0])
    dayEN = daysEN[j]
    # Search for a year beginning with dayEN (Sunday)
    for y in range(2020, 2000, -1):
        dt0101 = dt.datetime(y, 1, 1, 0, 0, 0, 0)
        if dt0101.weekday() == (j-1) % 7:
            break

    for i in range(len(df.index)):
        for j in range(len(df.values[0]) - 1):
            datetime_index = dt.datetime(y, 1, i + 1, j)
            indexValues.append(datetime_index)
            value = df.values[i][j + 1]
            values.append(value)

    placeNames.append(os.path.splitext(file)[0])
    placeValues.append(values)
    index1D = pd.Index(indexValues, name = "DayOfWeek_Time")
    df1D = pd.DataFrame(values, index = index1D, columns = [placeNames[l]])
    # df1D.to_csv(".\\data\\1D\\" + placeNames[l] + ".csv", header = True, encoding = "utf_8_sig")
    print(placeNames[l])

df1Ds = pd.DataFrame(np.transpose(placeValues), columns = placeNames, index = index1D)
df1Ds.to_csv(".\\data\\1D\\all.csv", header = True, encoding = "utf_8_sig")
print("Wrote all.csv")

