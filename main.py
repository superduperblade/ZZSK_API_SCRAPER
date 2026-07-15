from api.zzsk import train_API
import json

zssk_api = train_API()

zssk_api.queryStation("Bratislava")

#stations_in_radious = zssk_api.queryStationInRadius(latitude="48.18540811435552",longitude="17.134461445814082",radius_in_meters="25000",maxCount=20)
#print(stations_in_radious)

station1 = zssk_api.queryStation(station_name="Kosice",returnjson=True)
print(station1)

station2 = zssk_api.queryStation(station_name="Nitra",returnjson=True)
print(station2)

responce2 = zssk_api.queryTrainDelay(train_Number="616",TravelDate=1784110020000)
print(responce2)

responce1 = zssk_api.queryStationInRadius(latitude=48.30244677558488, longitude=18.079227198063098,radius_in_meters=25_000,maxCount=200,
                returnjson=True)
print(responce1)
routes = zssk_api.queryRoute(fromStation="5613600",toStation="5615306",returnjson=True)
with open("routes.json","w",encoding="utf-8") as f:
    json.dump(routes,f,indent=4,ensure_ascii=False)