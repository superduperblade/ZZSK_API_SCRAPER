import requests
import time
class train_API:
   
    API_KEY = r'PDh^2-$-M]8(dG8E+Q,FR}zsfz"Q~:N2pp\ykmg9ZEgKVrh42PHS?^sQ6<3;X,?-'
    API_BASE = "https://appn.zssk.sk/api/v4/"
    API_GET_STATION = API_BASE+"station/name/"
    API_GET_STATION_IN_RADIUS= API_BASE+"station/in-radius"
    API_GET_ROUTE = API_BASE + "route"
    headers = {
    "x-Api-Key": API_KEY,
    "platform": "and",
    "lang": "sk",
    "User-Agent": "okhttp"}



    def queryStation(self,station_name,maxCount=20):

        params = {"maxCount": maxCount}

        response = requests.get(
        self.API_GET_STATION+station_name,
        headers=self.headers,
        params=params)

        print("Status:", response.status_code)

        data = response.json()
        return data
    
    def queryStationInRadius(self,longitude,latitude,radius_in_meters=10_000,maxCount=20):

        ## the api returns 400 if radius_in_meters is beyond 25_000 meters warn the caller
        if int(radius_in_meters) > 25000:
            print("This is beyond the max amount likely to achive failure!")


        params = {  "maxCount":maxCount,
                    "latitude": latitude,
                    "longitude": longitude,
                    "radiusInMeters": radius_in_meters
            }
        response = requests.get(
        self.API_GET_STATION_IN_RADIUS,
        headers=self.headers,
        params=params)

        return response.json()
    
    def queryRoute(self,fromStation,toStation,departure=True,travelDate=str(int(time.time()*1000)),
        trainChange=True,maxChangeCount=2,minChangeTime=5,maxChangeTime=60,
        hasBicycle=False,hasChild=False,hasWheelchair=False):
        params = {
        "fromStation": fromStation,      # Bratislava hl.st.
        "toStation": toStation,        # example destination
        "departure": departure,
        "travelDate": travelDate,

        "trainChange": trainChange,

        "maxChangeCount": maxChangeCount,
        "minChangeTime": minChangeTime,
        "maxChangeTime": maxChangeTime,

        "bicycle": hasBicycle,
        "child": hasChild,
        "wheelChair": hasWheelchair}

        response = requests.get(
        self.API_GET_ROUTE,
        headers=self.headers,
        params=params)

        return response.json()