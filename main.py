from api.zzsk import train_API
import json

zssk_api = train_API()

zssk_api.queryStation("Bratislava")

#stations_in_radious = zssk_api.queryStationInRadius(latitude="48.18540811435552",longitude="17.134461445814082",radius_in_meters="25000",maxCount=20)
#print(stations_in_radious)



responce2 = zssk_api.queryTrainDelay(train_Number="745",TravelDate=1784151900000)
print(responce2.json())

routes = zssk_api.queryRoute(fromStation="5613600",toStation="5615306",returnjson=True)
with open("routes.json","w",encoding="utf-8") as f:
    json.dump(routes,f,indent=4,ensure_ascii=False)