import sys
import os
import pandas as pd
import geopandas as gpd
import datetime as dt
import populartimes as pt
import numpy as np

print(sys.version)
print(os.getcwd())


# annual users at stations
# data of 2018
xml = ".\\rawData\\S12-19.xml"
shape = ".\\rawData\\S12-19_NumberOfPassengers.shp"
dbf = ".\\rawData\\S12-19_NumberOfPassengers.dbf"
gdf = gpd.read_file(dbf, encoding='shift-jis')

StationColumn = 'S12_001'
LineColumn = 'S12_003'
UsersInOutColumn = []
UsersInOutColumn_exists = []
UsersInOutColumn_overlap = []
UsersInOut_pastAvg = []
for y in range(2011, 2019):
    suffix = 4 * (y - 2011) + 9
    UsersInOutColumn.append([y, 'S12_' + str(suffix).zfill(3)])
    UsersInOutColumn_exists.append([y, 'S12_' + str(suffix-2).zfill(3)]) # 1: exist, 2: not exist
    UsersInOutColumn_overlap.append([y, 'S12_' + str(suffix-3).zfill(3)]) # 1: main, 2: sub

# Irregular cases
gdf.loc[(gdf[StationColumn] == '京成高砂') & (gdf[LineColumn] == '金町線'), UsersInOutColumn_overlap[2016 - 2011][1]] = 2
# 綾瀬駅のJR常磐緩行線/千代田線は乗り入れしているので原理的に2つの乗降者数の仕分けは出来ない
for UsersInOutColumn_overlap_entry in UsersInOutColumn_overlap:
    gdf.loc[(gdf[StationColumn] == '綾瀬') & (gdf[LineColumn] == '常磐線'), UsersInOutColumn_overlap_entry[1]] = 2

# 更に綾瀬駅の国土地理院の乗降者数は、千代田線から直通して常磐緩行線に載った人（綾瀬駅から降りない）も含まれるので、足立区の統計で書き換える：
# https://www.city.adachi.tokyo.jp/kuse/ku/aramashi/toke-suji.html
    gdf.loc[(gdf[StationColumn] == '綾瀬') & (gdf[LineColumn] == '9号線千代田線'), UsersInOutColumn_exists[2011 - 2011][1]] = 2
    gdf.loc[(gdf[StationColumn] == '綾瀬') & (gdf[LineColumn] == '9号線千代田線'), UsersInOutColumn_exists[2012 - 2011][1]] = 2
    gdf.loc[(gdf[StationColumn] == '綾瀬') & (gdf[LineColumn] == '9号線千代田線'), UsersInOutColumn_exists[2013 - 2011][1]] = 2
    gdf.loc[(gdf[StationColumn] == '綾瀬') & (gdf[LineColumn] == '9号線千代田線'), UsersInOutColumn[2014 - 2011][1]] = 87767
    gdf.loc[(gdf[StationColumn] == '綾瀬') & (gdf[LineColumn] == '9号線千代田線'), UsersInOutColumn[2015 - 2011][1]] = 86666
    gdf.loc[(gdf[StationColumn] == '綾瀬') & (gdf[LineColumn] == '9号線千代田線'), UsersInOutColumn[2016 - 2011][1]] = 87457
    gdf.loc[(gdf[StationColumn] == '綾瀬') & (gdf[LineColumn] == '9号線千代田線'), UsersInOutColumn[2017 - 2011][1]] = 88393
    gdf.loc[(gdf[StationColumn] == '綾瀬') & (gdf[LineColumn] == '9号線千代田線'), UsersInOutColumn[2018 - 2011][1]] = 89649

placeIDTable = [
        #['京成高砂', 'ChIJkytGpZGFGGARHPYdFQUpePg'],
        #['亀有', 'ChIJS0xMA4-PGGARrhRopbLAjJE'],
        #['綾瀬', 'ChIJR-uLzLmPGGARdKB5dcBQhAQ'],
        #['金町', 'ChIJE25z-3OFGGARfZM79XK_aso'], # 金町のGoogle Mapの混雑度のデータが明らかにおかしい(夕方ピークが無い、駅が閉じている深夜3時の方が多い曜日がある)。綾瀬、亀有、松戸は共通して、土日の落ち込みが京成線程顕著でない、夕ビークと朝ピークの高さが同程度、だったので、金町も同様と仮定し、亀有のデータを代用する。
        ['金町', 'ChIJS0xMA4-PGGARrhRopbLAjJE'],
        #['京成金町', 'ChIJyclIG3SFGGARdie31Z4pIs0'],
        #['堀切菖蒲園', 'ChIJsewEZKePGGAR61vD6DkQsHk'],
        #['お花茶屋', 'ChIJ6a9LTHGPGGARl4SEYCeMiVE'],
        #['四ツ木', 'ChIJSVpcHUCPGGARsETzsZ-zsSs'],
        ##['京成立石', 'ChIJc-paQWePGGAR0iqCYP6FalU'], # for some reason, library "populartime" fails to fetch popular times although the information can be seen from browser, to be addressed later
        #['京成立石', 'ChIJ6a9LTHGPGGARl4SEYCeMiVE'], # so, temporary we use a similar profile of お花茶屋
        #['青砥', 'ChIJ0zXlk4mFGGAR-DpjbGMTwRg'],
        #['柴又', 'ChIJ8ZLvWL2FGGAR9SlVGqXXMOY'],
        #['新柴又', 'ChIJc3DfO7-FGGARUac9rfbgQO0'],
        #['京成小岩', 'ChIJD-P0y9qFGGARQLiuhAfdnVE'],
        #['小岩', 'ChIJPTE1ltiFGGARjcyWPezhxiw'],
        #['新小岩', 'ChIJzchyvAOGGGARnwjiB9Wa31U']
    ]
placeIDTableZip = list(zip(*placeIDTable))
stations = placeIDTableZip[0]
placeIDs = placeIDTableZip[1]
UsersInOut = []

for station in stations:
    gdf_station = gdf[gdf[StationColumn]==station]
    user = [None] * len(UsersInOutColumn)
    for i in range(0, len(UsersInOutColumn)):
        gdf_filtered = gdf_station[(gdf_station[UsersInOutColumn_exists[i][1]] == 1) & (gdf_station[UsersInOutColumn_overlap[i][1]] == 1)]
        if len(gdf_filtered) == 0:
            user[i] = None
        elif len(gdf_filtered) == 1:
            user[i] = gdf_filtered[UsersInOutColumn[i][1]].values[0]
        else:
            raise ValueError("Duplicated entries of " + station + " for year " + str(UsersInOutColumn[i][0]))
    # take the latest number as Google Mobility Reports set their baseline the median during Jan 3 - Feb 6 2020.
    # https://www.google.com/covid19/mobility/data_documentation.html?hl=en
    for i in range(len(UsersInOutColumn)-1, -1, -1):
        if(user[i] != None):
            users = user[i]
            break
    if i == -1:
        raise ValueError("Station " + station + " numbers of in/out users are None for all years")
    UsersInOut.append([station, users])

# mobility report from Google
today = dt.datetime.now()
thisYear = today.year
mobilityFile = ".\\rawData\\" + str(thisYear) + "_JP_Region_Mobility_Report.csv"
mobilityCSV = pd.read_csv(mobilityFile)

mobilities_weeekly_ave = []
for station in stations:
    mobilityCSV_area = mobilityCSV[(mobilityCSV['sub_region_1'] == 'Tokyo')]
    mobilityCSV_station = mobilityCSV_area['transit_stations_percent_change_from_baseline']
    mobility_weekly_avg = 1.0 + mobilityCSV_station[-7:].mean() / 100.0
    mobilities_weeekly_ave.append(mobility_weekly_avg)
    
# Popular time by Google Map
google_api_key = "[Your Google Cloud API Key]"
placeInfos = []
for i in range(len(stations)):
    placeInfo = pt.get_id(google_api_key, placeIDs[i])
    if "populartimes" not in placeInfo:
        print("no populartimes for " + stations[i])
    placeInfos.append(placeInfo)

# compute estimation and save to csv for each station
daysJP = ['日曜日', '月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日']
daysEN = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

placeEstimated = []
for i in range(len(stations)):
    estimated_for_week = 7 * UsersInOut[i][1] * mobilities_weeekly_ave[i]
    placeInfo = placeInfos[i]
    popularTime = placeInfo['populartimes']
    popularTimeValues = []
    for j in range(len(daysEN)):
        for k in range(len(popularTime)):
            if daysEN[j] == popularTime[k]['name']:
                popularTimeValues.append(np.array(popularTime[k]['data']))
                break

    popularTimeDaily = []
    for j in range(len(daysEN)):
        popularTimeDaily.append(sum(popularTimeValues[j]))
    placeEstimated = []
    for j in range(len(daysEN)):
        popularTimeNormalized = popularTimeValues[j] / sum(popularTimeDaily)
        estimated = estimated_for_week * popularTimeNormalized
        placeEstimated.append(estimated)

    df = pd.DataFrame(placeEstimated, index = daysJP)
    df.name = stations[i]
    df = df.astype(int)
    csvFile = ".\\data\\original\\" + stations[i] + ".csv"
    df.to_csv(csvFile, encoding = 'utf_8_sig')
    
    print("Finished: " + stations[i])

print("Done")
