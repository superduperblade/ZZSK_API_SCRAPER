import math
import time
import pandas as pd
import requests
import sys
import os
from pathlib import Path
from datetime import datetime
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api.zzsk import train_API
import zstandard as zstd

zzsk_api = train_API()

DUMP_DIR = "./data_dump"
POLL_INTERVAL_SEC = 30


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
def compress(content):
    data = json.dumps(content).encode("utf-8")
    compressor = zstd.ZstdCompressor(level=3)
    compressed_data = compressor.compress(data)
    return compressed_data


def save_response(origin, destination, response):

    now = datetime.utcnow()

    folder = (
        Path("data/raw")
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

    with open(folder / filename, "wb", encoding="utf8") as f:
        compress(data=json.dump(response, f, indent=4, ensure_ascii=False))







def main():
    if not os.path.exists(DUMP_DIR):
        os.makedirs(DUMP_DIR)
    

  

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
                
       

        print(f"Cycle complete. ") 
        print(f"Sleeping for {POLL_INTERVAL_SEC / 60} minutes...\n") 
        
        time.sleep(POLL_INTERVAL_SEC)



main()