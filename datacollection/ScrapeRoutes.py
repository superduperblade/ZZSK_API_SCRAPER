"""
Route Scraper for ZSSK API.

Continuously collects route data between predefined station pairs
and saves them to compressed JSON files.
"""
import math
import time
import pandas as pd
import requests
import sys
import os
from pathlib import Path
from datetime import datetime
import json
import zstandard as zstd
import argparse
import csv
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api.zzsk import train_API
from proccessing.JsonValidator import JsonValidator
zzsk_api = train_API()

DUMP_DIR = "data/raw"
MAX_RANDOM_STAIONS = 20
POLL_INTERVAL_SEC = 30
RANDOM_ROUTE_POLL_INTERVAL_SEC = 500

ROUTES = [
    # 1-4: Main Corridor
    ("5613206", "5613600"), ("5613600", "5613206"), # Bratislava hl.st. <-> Košice
    ("5613206", "5617915"), ("5617915", "5613206"), # Bratislava hl.st. <-> Žilina
    
    # 5-9: Smižany (using Spišská Nová Ves 5613616 as the hub)
    ("5613616", "5613600"), ("5613600", "5613616"), # Košice <-> Smižany (SNV)
    ("5613616", "5614946"), ("5614946", "5613616"), # Poprad-Tatry <-> Smižany (SNV)
    ("5613616", "5613206"),                         # Bratislava <-> Smižany (SNV)
    
    # 10-50: Major Hub Connections
    ("5613206", "5613186"), ("5613186", "5613206"), # Bratislava <-> Trnava
    ("5613206", "5614746"), ("5614746", "5613206"), # Bratislava <-> Trenčín
    ("5617915", "5613486"), ("5613486", "5617915"), # Žilina <-> Vrútky
    ("5617915", "5613586"), ("5613586", "5617915"), # Žilina <-> Považská Bystrica
    ("5613600", "5613560"), ("5613560", "5613600"), # Košice <-> Kysak
    ("5613600", "5613530"), ("5613530", "5613600"), # Košice <-> Prešov
    ("5614946", "5617915"), ("5617915", "5614946"), # Poprad-Tatry <-> Žilina
    ("5613206", "5614486"), ("5614486", "5613206"), # Bratislava <-> Nitra
    ("5614746", "5614536"), ("5614536", "5614746"), # Trenčín <-> Prievidza
    ("5613406", "5613416"), ("5613416", "5613406"), # Zvolen <-> Banská Bystrica
    ("5617915", "5613416"), ("5613416", "5617915"), # Žilina <-> Banská Bystrica
    ("5613600", "5614946"), ("5614946", "5613600"), # Košice <-> Poprad-Tatry
    ("5613206", "5613146"), ("5613146", "5613206"), # Bratislava <-> Galanta
    ("5613186", "5614746"), ("5614746", "5613186"), # Trnava <-> Trenčín
    ("5613600", "5613540"), ("5613540", "5613600"), # Košice <-> Trebišov
    ("5613600", "5613550"), ("5613550", "5613600"), # Košice <-> Michalovce
    ("5613206", "5613226"), ("5613226", "5613206"), # Bratislava <-> Pezinok
    ("5613600", "5613580"), ("5613580", "5613600"), # Košice <-> Čierna nad Tisou
    ("5617915", "5614776"), ("5614776", "5617915"), # Žilina <-> Čadca
]

train_stations = []

parser = argparse.ArgumentParser()
parser.add_argument("-o","--Output",help="location of output directory",default=DUMP_DIR)
parser.add_argument("-cl","--CompressionLevel",help="level to compress json at using zstandard",default=4)
parser.add_argument("-csv","--csv",help="location of the train station csv to use to pull random routes",default="train-station.csv")
args = parser.parse_args()


def readTrainStaions_csv(csv_path):
    with open(csv_path,newline="") as f:
        reader = csv.reader(f)
        return list(reader)


def generateRandomRouteList(station_list,amount,maxRange=None):
    if maxRange == None:
        maxRange = len(station_list)
    
   
   
    random_station_list = [] 
    for i in range(amount):
        random_station_list.append(genreateRandomRoute(station_list=station_list,maxRange=maxRange))
    return random_station_list
           
            

    
def genreateRandomRoute(station_list,maxRange):
    isStationValid = False
    jvalid = JsonValidator()
    while isStationValid == False:
        
            r1 = random.randint(1,maxRange)
            r2 = random.randint(1,maxRange)
            station_1 = station_list[r1]
            station_1_uuic_code = station_list[0]
        
            station_2 = station_list[r2]
            stations_2_uuic_code = station_list[0]
            
            print("station1: ",station_1)
            print("station2: ",station_2)
            try: 
                result = zzsk_api.queryRoute(fromStation=station_1_uuic_code,toStation=stations_2_uuic_code,returnjson=True)
            except:
                ##to do show error and correctly look for conection closed which equals rate limit
                print("Waiting 10 seconds encountered a error")
                time.sleep(10)
                result = zzsk_api.queryRoute(fromStation=station_1_uuic_code,toStation=stations_2_uuic_code,returnjson=True)
            if jvalid.isJsonEmpty(content=result) == False:
                isStationValid = True
                return(station_1_uuic_code,stations_2_uuic_code)
def compress(content):
    """
    Compress JSON content using Zstandard compression.
    
    Args:
        content: Data to compress (will be JSON serialized).
    
    Returns:
        bytes: Compressed data.
    """
    data = json.dumps(content).encode("utf-8")
    compressor = zstd.ZstdCompressor(level=args.CompressionLevel)
    compressed_data = compressor.compress(data)
    return compressed_data


def save_response(origin, destination, response):
    """
    Save route response to a compressed JSON file.
    
    Creates a directory structure: output/YYYY/MM/DD/
    Filename format: YYYYMMDD_HHMMSS_origin_destination.json
    
    Args:
        origin (str): Origin station ID.
        destination (str): Destination station ID.
        response (dict): Route data to save.
    """
    now = datetime.utcnow()

    folder = (
        Path(args.Output)
        / str(now.year)
        / f"{now.month:02d}"
        / f"{now.day:02d}"
    )

    folder.mkdir(parents=True, exist_ok=True)
    
    safe_origin = "".join(c if c.isalnum() else "_" for c in origin)
    safe_destination = "".join(c if c.isalnum() else "_" for c in destination)
    filename = (
        f"{now.strftime('%Y%m%d_%H%M%S')}_"
        f"{safe_origin.replace(' ','_')}_"
        f"{safe_destination.replace(' ','_')}.json"
    )
    
    content = json.dumps(response, indent=4, ensure_ascii=False)
    content_bytes = content.encode("utf-8")

    with open(folder / filename, "wb") as f:
        f.write(compress(content=content))






random_station_list = readTrainStaions_csv(args.csv)

def main():
    if not os.path.exists(DUMP_DIR):
        os.makedirs(DUMP_DIR)
    

    counter = 1
    random_Routes = generateRandomRouteList(station_list=random_station_list,amount=MAX_RANDOM_STAIONS)
    while True:
        current_time_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        print(f"--- Starting cycle at {current_time_str} ---")
        cycle_data = [] 
        errors = []
       

        for origin,destination in ROUTES:
            print(f"saving {origin} --> {destination} route")

            try:
                route_responce = zzsk_api.queryRoute(fromStation=origin,toStation=destination,returnjson=True)
                save_response(origin=origin,destination=destination,response=route_responce)
                print("Responce saved")
            except Exception  as e:
                print("ERROR: ",e)
                
        for origin,destination in ramdom_Routes:
            print(f"saving {origin} --> {destination} route")

            try:
                route_responce = zzsk_api.queryRoute(fromStation=origin,toStation=destination,returnjson=True)
                save_response(origin=origin,destination=destination,response=route_responce)
                print("Responce saved")
            except Exception  as e:
                print("ERROR: ",e)
                

        print(f"Cycle complete. ") 
        print(f"Sleeping for {POLL_INTERVAL_SEC / 60} minutes...\n") 
        
        time.sleep(POLL_INTERVAL_SEC)
        counter += 1 
        if counter ==5:
            counter = 0
            generateRandomRouteList(station_list=random_Routes,amount=MAX_RANDOM_STAIONS)

main()