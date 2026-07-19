import requests
import time


class train_API:
    """
    Client for the ZSSK (Slovak Railways) API.
    
    Provides methods to query train stations, routes, and delay information
    from the ZSSK mobile API.
    
    Attributes:
        API_KEY (str): API key for authentication.
        API_BASE (str): Base URL for the API.
        headers (dict): Default headers for API requests.
    """
   
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


    def queryStation(self, station_name, maxCount=20, returnjson=False):
        """
        Search for stations by name.
        
        Args:
            station_name (str): Name of the city, town, or village to search for.
            maxCount (int): Maximum number of results to return. Default: 20.
            returnjson (bool): If True, returns parsed JSON; otherwise returns raw response.
        
        Returns:
            list or requests.Response: List of stations with names and coordinates,
                or raw response object if returnjson=False.
        """
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
    def queryStationInRadius(self, longitude, latitude, radius_in_meters=10_000, maxCount=20, returnjson=False):
        """
        Find stations within a radius from specified coordinates.
        
        Args:
            longitude (str): Longitude coordinate.
            latitude (str): Latitude coordinate.
            radius_in_meters (int): Search radius in meters. Max: 25,000. Default: 10,000.
            maxCount (int): Maximum number of results. Default: 20.
            returnjson (bool): If True, returns parsed JSON; otherwise returns raw response.
        
        Returns:
            list or requests.Response: List of stations with names and coordinates.
        
        Note:
            The API returns 400 error if radius exceeds 25,000 meters.
        """
        if int(radius_in_meters) > 25000:
            print("This is beyond the max amount likely to achive failure!")

        params = {
            "maxCount": maxCount,
            "latitude": latitude,
            "longitude": longitude,
            "radiusInMeters": radius_in_meters
        }
        response = requests.get(
        self.API_GET_STATION_IN_RADIUS,
        headers=self.headers,
        params=params)

        return response.json()
    
    def queryRoute(self, fromStation, toStation, departure=True, travelDate=str(int(time.time()*1000)),
        trainChange=True, maxChangeCount=2, minChangeTime=5, maxChangeTime=60,
        hasBicycle=False, hasChild=False, hasWheelchair=False, returnjson=False):
        """
        Get train routes between two stations.
        
        Args:
            fromStation (str): Origin station ID.
            toStation (str): Destination station ID.
            departure (bool): True for departure time, False for arrival. Default: True.
            travelDate (str): Unix timestamp in milliseconds. Default: current time.
            trainChange (bool): Allow train changes. Default: True.
            maxChangeCount (int): Maximum number of train changes. Default: 2.
            minChangeTime (int): Minimum change time in minutes. Default: 5.
            maxChangeTime (int): Maximum change time in minutes. Default: 60.
            hasBicycle (bool): Require bicycle transport. Default: False.
            hasChild (bool): Require child facilities. Default: False.
            hasWheelchair (bool): Require wheelchair access. Default: False.
            returnjson (bool): If True, returns parsed JSON; otherwise returns raw response.
        
        Returns:
            list or requests.Response: List of route options with details.
        """
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
    def queryNextRoute(self, connectionNextInfo, connectionNextTime, returnjson=False):
        """
        Get next route information.
        
        Args:
            connectionNextInfo (str): Connection next info parameter.
            connectionNextTime (str): Connection next time parameter.
            returnjson (bool): If True, returns parsed JSON; otherwise returns raw response.
        
        Returns:
            list or requests.Response: Next route information.
        """
        params = {
            "connectionNextInfo": connectionNextInfo,
            "connectionNextTime": connectionNextTime
        }
        response = requests.get(
        self.API_GET_ROUTE_NEXT,
        headers=self.headers,
        params=params)
        if returnjson:
            return response.json()
        else:
            return response

    def queryPreviousRoute(self, connectionPrevInfo, connectionPrevTime, returnjson=False):
        """
        Get previous route information.
        
        Args:
            connectionPrevInfo (str): Connection previous info parameter.
            connectionPrevTime (str): Connection previous time parameter.
            returnjson (bool): If True, returns parsed JSON; otherwise returns raw response.
        
        Returns:
            list or requests.Response: Previous route information.
        """
        params = {
            "connectionPrevInfo": connectionPrevInfo,
            "connectionPrevTime": connectionPrevTime
        }
        response = requests.get(
        self.API_GET_ROUTE_PREV,
        headers=self.headers,
        params=params)
        if returnjson:
            return response.json()
        else:
            return response

    def queryTrainDelay(self, train_Number, TravelDate, returnjson=False):
        """
        Get delay information for a specific train.
        
        Args:
            train_Number (str): Train number to query.
            TravelDate (int): Unix timestamp in milliseconds for the travel date.
            returnjson (bool): If True, returns parsed JSON; otherwise returns raw response.
        
        Returns:
            dict or requests.Response: Delay information including delay minutes,
                current station, and next/previous stations.
        """
        body = {
            "travelDate": TravelDate,
            "trainNumber": train_Number
        }
        
        responce = requests.get(self.API_GET_DELAY,
        headers=self.headers,
        params=body)

        if returnjson:
            return responce.json()
        else:
            return responce
        
