#!/usr/bin/env python3
"""
Query the ZSSK train delay API with real (trainNumber, travelDate) pairs
pulled from a routes.json route-search response.

Usage:
    python zssk_delay_check.py routes.json
    python zssk_delay_check.py routes.json --poll 300   # poll every 5 min until non-empty
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone

import requests

DELAY_URL = "https://appn.zssk.sk/api/v4/train/delay"
HEADERS = {"Content-Type": "application/json"}


def extract_pairs(routes_path):
    """
    Pull (trainNumber, departureTimestamp) pairs from every route segment.
    NOTE: this uses the segment's own departureTimestamp, which may be a
    mid-route boarding point rather than the train's true origin station.
    See build_origin_pairs() below for the origin-station version.
    """
    with open(routes_path) as f:
        data = json.load(f)

    pairs = []
    seen = set()
    for route in data:
        for seg in route.get("routeSegments", []):
            train = seg.get("train")
            ts = seg.get("departureTimestamp")
            if train and train.get("number") and ts:
                key = (train["number"], ts)
                if key not in seen:
                    seen.add(key)
                    pairs.append(key)
    return pairs


def extract_origin_pairs(routes_path):
    """
    Pull (trainNumber, departureTimestamp) using the FIRST trainStop in each
    segment's trainStops list -- i.e. the train's actual origin-station
    departure, which is what the delay backend likely keys on.
    """
    with open(routes_path) as f:
        data = json.load(f)

    pairs = []
    seen = set()
    for route in data:
        for seg in route.get("routeSegments", []):
            train = seg.get("train")
            stops = seg.get("trainStops") or []
            if not train or not train.get("number") or not stops:
                continue
            first_stop = stops[0]
            ts = first_stop.get("departureTimestamp")
            if ts:
                key = (train["number"], ts)
                if key not in seen:
                    seen.add(key)
                    pairs.append(key)
    return pairs


def query_delays(pairs):
    body = [{"trainNumber": num, "travelDate": ts} for num, ts in pairs]
    resp = requests.post(DELAY_URL, headers=HEADERS, json=body, timeout=15)
    resp.raise_for_status()
    return resp.json()


def fmt(ts_ms):
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("routes_json", help="Path to a saved route-search response")
    ap.add_argument("--origin", action="store_true",
                     help="Use origin-station departure timestamps instead of segment timestamps")
    ap.add_argument("--poll", type=int, default=0,
                     help="Re-query every N seconds until a non-empty result is returned")
    args = ap.parse_args()

    pairs = extract_origin_pairs(args.routes_json) if args.origin else extract_pairs(args.routes_json)
    if not pairs:
        print("No (trainNumber, timestamp) pairs found in the file.", file=sys.stderr)
        sys.exit(1)

    print(f"Querying {len(pairs)} train/timestamp pairs:")
    for num, ts in pairs:
        print(f"  train {num:>6}  ->  {fmt(ts)}")
    print()

    while True:
        result = query_delays(pairs)
        stamp = datetime.now().strftime("%H:%M:%S")
        if result:
            print(f"[{stamp}] Got {len(result)} delay record(s):")
            for entry in result:
                num = entry.get("trainNumber")
                delay = entry.get("trainDelay")
                if delay:
                    mins = delay.get("delayMinutes")
                    cur = delay.get("currentName")
                    nxt = delay.get("nextStationName")
                    prev = delay.get("previousStationName")
                    arrived = delay.get("arrivedAtDestination")
                    snap_ts = delay.get("timestamp")
                    snap = fmt(snap_ts) if snap_ts else "?"
                    status = "arrived at destination" if arrived else f"between {prev} -> {nxt}"
                    print(f"  train {num:>6}  delay {mins:>3} min  ({status}, near {cur})  [as of {snap}]")
                else:
                    print(f"  train {num:>6}  no delay data in response: {entry}")
            print()
            print("Raw JSON:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            break
        else:
            print(f"[{stamp}] Empty response ([])" + (" -- retrying..." if args.poll else ""))
            if not args.poll:
                break
            time.sleep(args.poll)


if __name__ == "__main__":
    main()