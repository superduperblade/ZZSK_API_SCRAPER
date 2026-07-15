import math
import time
import pandas as pd
import requests
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api.zzsk import train_API


# Gets all the slovak stations
# ---------------------------------------------------------------------------
# 1. CONFIG - edit these
# ---------------------------------------------------------------------------
 

RADIUS_M = 25000                            # 25 km, per your API
REQUEST_DELAY_SEC = 0.2                 
 
# Slovakia bounding box (approx, with a little padding)
LAT_MIN, LAT_MAX = 47.70, 49.65
LON_MIN, LON_MAX = 16.80, 22.60
 
OUTPUT_XLSX = "./slovakia_stations.xls"
zssk_api = train_API()

def generate_grid(lat_min, lat_max, lon_min, lon_max, radius_m, overlap_factor=0.8):
    """
    Generate a lat/lon grid of points such that circles of `radius_m`
    around each point fully cover the bounding box, with some overlap
    so nothing slips through near the edges.
 
    overlap_factor < 1 means points are closer together than the
    "perfect tiling" distance, giving safety margin. 0.8 is generally
    a safe, not-too-wasteful choice.
    """
    # Distance between grid points (meters), using overlap factor
    step_m = radius_m * math.sqrt(2) * overlap_factor
 
    # Convert step to degrees
    lat_step_deg = step_m / 111_320  # ~meters per degree latitude, constant
 
    points = []
    lat = lat_min
    row = 0
    while lat <= lat_max:
        # meters per degree longitude shrinks as you go north -> recompute per row
        meters_per_deg_lon = 111_320 * math.cos(math.radians(lat))
        lon_step_deg = step_m / meters_per_deg_lon
 
        # Offset alternate rows by half a step (hex-ish packing -> fewer points)
        lon_offset = lon_step_deg / 2 if row % 2 else 0
 
        lon = lon_min - lon_offset
        while lon <= lon_max:
            points.append((round(lat, 5), round(lon, 5)))
            lon += lon_step_deg
 
        lat += lat_step_deg
        row += 1
 
    return points
 
def main():
        grid_points = generate_grid(LAT_MIN, LAT_MAX, LON_MIN, LON_MAX, RADIUS_M)
        print(f"Generated {len(grid_points)} grid points to query.")
        all_stations = {}   # keyed by unique station id to dedupe
        errors = []
        for i, (lat, lon) in enumerate(grid_points, start=1):
            try:
                stations = zssk_api.queryStationInRadius(latitude=lat, longitude=lon,radius_in_meters=25_000,maxCount=200,
                returnjson=True)
            except Exception as e:
                errors.append({"lat": lat, "lon": lon, "error": str(e)})
                print(f"[{i}/{len(grid_points)}] ERROR at ({lat}, {lon}): {e}")
                time.sleep(REQUEST_DELAY_SEC)
                continue
        
            for s in stations:
            # ADJUST: pick whatever field is the unique station identifier.
            # Falls back to (name, lat, lon) if no id field exists.
                station_id = (
                s.get("uicCode")
                or s.get("station_id")
                or s.get("code")
                or (s.get("name"), s.get("lat"), s.get("lon"))
            )
                all_stations[station_id] = s  # dict dedupe: last write wins
 
        print(f"[{i}/{len(grid_points)}] ({lat}, {lon}) -> "
              f"{len(stations)} stations (total unique so far: {len(all_stations)})")
 
        time.sleep(REQUEST_DELAY_SEC)
 
    # ---------------------------------------------------------------------
    # 5. EXPORT
    # ---------------------------------------------------------------------
        df = pd.DataFrame(list(all_stations.values()))
        print(f"\nTotal unique stations found: {len(df)}")
 
        with pd.ExcelWriter(OUTPUT_XLSX, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="stations", index=False)
            if errors:
                pd.DataFrame(errors).to_excel(writer, sheet_name="errors", index=False)
 
        print(f"Saved to {OUTPUT_XLSX}")
 
 
if __name__ == "__main__":
    main()
