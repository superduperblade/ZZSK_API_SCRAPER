import requests
import time
class train_API:
   
    API_KEY = r'PDh^2-$-M]8(dG8E+Q,FR}zsfz"Q~:N2pp\ykmg9ZEgKVrh42PHS?^sQ6<3;X,?-'
    
    API_BASE = "https://appn.zssk.sk/api/v4/"
    API_GET_STATION = API_BASE+"station/name/"
    API_GET_STATION_IN_RADIUS= API_BASE+"station/in-radius"
    API_GET_ROUTE = API_BASE + "route"
    API_GET_ROUTE_NEXT = API_BASE + "route/next"
    API_GET_ROUTE_PREV = API_BASE + "route/previous"
    API_GET_DELAY = API_BASE + "train/delay"


    headers = {
    "x-Api-Key": API_KEY,
    "platform": "and",
    "lang": "sk",
    "User-Agent": "okhttp",
    "Content-Type": "application/json"}


    # Gets a list of stations in a city/town/villiage and their names and cordinates
    def queryStation(self,station_name,maxCount=20,returnjson=False):

        params = {"maxCount": maxCount}

        response = requests.get(
        self.API_GET_STATION+station_name,
        headers=self.headers,
        params=params)

        print("Status:", response.status_code)  

        if returnjson:
          return response.json()
        else:
            return response
    #Gets a list of stations in a radius from a specifed longitude and latitude in a specified radius returns names and coordinates
    def queryStationInRadius(self,longitude,latitude,radius_in_meters=10_000,maxCount=20,returnjson=False):

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
    
    # Gets train routes from one station to another including being able to sort by query info
    def queryRoute(self,fromStation,toStation,departure=True,travelDate=str(int(time.time()*1000)),
        trainChange=True,maxChangeCount=2,minChangeTime=5,maxChangeTime=60,
        hasBicycle=False,hasChild=False,hasWheelchair=False,returnjson=False):
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

        if returnjson:
            return response.json()
        else:
            return response
    def queryNextRoute(self,connectionNextInfo,connectionNextTime):
        params={
            "connectionNextInfo": connectionNextInfo,
            "connectionNextTime" : connectionNextTime
        }
        response = requests.get(
        self.API_GET_ROUTE_NEXT,
        headers=self.headers,
        params=params)
        if returnjson:
            return response.json()
        else:
            return response

    def queryPreviousRoute(self,connectionPrevInfo,connectionPrevTime,returnjson=False):
        params={
            "connectionPrevInfo": connectionNextInfo,
            "connectionPrevTime" : connectionNextTime
        }
        response = requests.get(
        self.API_GET_ROUTE_PREV,
        headers=self.headers,
        params=params)
        if returnjson:
            return response.json()
        else:
            return response

    #use the train number to get a delay of its route
    def queryTrainDelay(self,train_Number,TravelDate,returnjson=False):
        body = {
            "travelDate": TravelDate,
            "trainNumber": train_Number
        }
        
        responce = requests.get(self.API_GET_ROUTE,
        headers=self.headers,
        json=body)

        if returnjson:
            return responce.json()
        else:
            return responce
        
