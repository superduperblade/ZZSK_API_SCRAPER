# ZZSK API Scraper

A Python library and toolkit for interacting with the ZSSK (Slovak Railways) API to retrieve train schedules, station information, and delay data.

## Overview

This project provides tools to:
- Query train stations by name or location
- Find routes between stations
- Check train delays in real-time
- Collect and store route data for analysis
- Export station data to Excel format

## Installation

```bash
pip install -r requirements.txt
```

### Requirements
- Python 3.8+
- requests
- pandas
- openpyxl
- zstandard

## Project Structure

```
railway-test/
├── api/
│   └── zzsk.py           # Main API wrapper class
├── datacollection/
│   ├── ScrapeRoutes.py   # Continuous route data scraper
│   ├── slovakiastations.py # Station data collector
│   └── proccessing/
│       └── JsonValidator.py  # JSON validation and cleanup tool
├── main.py               # Example usage
├── test.py               # Train delay query script
├── requirements.txt
└── README.md
```

## API Usage

### Basic Setup

```python
from api.zzsk import train_API

# Initialize the API client
zssk_api = train_API()
```

### Station Queries

#### Search Stations by Name

```python
# Get stations matching a name (e.g., "Bratislava")
response = zssk_api.queryStation("Bratislava", maxCount=20, returnjson=True)
# Returns list of stations with names and coordinates
```

#### Find Stations in Radius

```python
# Find stations within a radius from coordinates
stations = zssk_api.queryStationInRadius(
    latitude="48.18540811435552",
    longitude="17.134461445814082",
    radius_in_meters=25000,
    maxCount=20,
    returnjson=True
)
```

**Note:** The API has a maximum radius limit of 25,000 meters.

### Route Queries

```python
# Get routes between two stations
routes = zssk_api.queryRoute(
    fromStation="5613600",  # Origin station ID
    toStation="5615306",    # Destination station ID
    departure=True,         # True for departure, False for arrival
    travelDate=str(int(time.time()*1000)),  # Unix timestamp in milliseconds
    trainChange=True,
    maxChangeCount=2,
    minChangeTime=5,
    maxChangeTime=60,
    hasBicycle=False,
    hasChild=False,
    hasWheelchair=False,
    returnjson=True
)
```

### Train Delay Queries

```python
# Check delay for a specific train
delay = zssk_api.queryTrainDelay(
    train_Number="745",
    TravelDate=1784151900000,  # Unix timestamp in milliseconds
    returnjson=True
)
```

## Data Collection Tools

### ScrapeRoutes.py

Continuously collects route data and saves it to compressed JSON files.

```bash
python datacollection/ScrapeRoutes.py
```

**Options:**
- `-o, --Output` - Output directory (default: `data/raw`)
- `-cl, --CompressionLevel` - Zstandard compression level (default: 4)

**Output:** Creates a directory structure `data/raw/YYYY/MM/DD/` with timestamped JSON files.

### slovakiastations.py

Collects all Slovak railway stations and exports them to Excel.

```bash
python datacollection/slovakiastations.py
```

**Configuration (edit in file):**
- `RADIUS_M` - Search radius in meters (default: 25,000)
- `REQUEST_DELAY_SEC` - Delay between API requests (default: 0.2)
- `OUTPUT_XLSX` - Output Excel file path (default: `./slovakia_stations.xls`)

**How it works:**
1. Generates a grid of latitude/longitude points covering Slovakia
2. Queries the API for stations in each grid point
3. Deduplicates results by station ID
4. Exports to Excel with optional error log sheet

### JsonValidator.py

Validates and removes empty JSON files from the data collection.

```bash
python datacollection/proccessing/JsonValidator.py -i data/raw
```

**Options:**
- `-i, --input` - Parent directory to process (required)
- `-dc, --decompress` - Decompress files before validation (default: True)
- `--no_delete` - Don't delete empty files, just report them

## Test Script (test.py)

Queries train delay information from a saved routes.json file.

```bash
# Basic usage
python test.py routes.json

# Use origin-station timestamps
python test.py routes.json --origin

# Poll every 5 minutes until non-empty result
python test.py routes.json --poll 300
```

## Station IDs Reference

Common Slovak station IDs used in the project:
- `5613600` - Bratislava hl.st. (main station)
- `5613206` - Bratislava
- `5617915` - Žilina
- `5613616` - Košice
- `5614946` - Poprad-Tatry
- `5614746` - Trenčín
- `5613186` - Trnava
- `5613486` - Vrútky
- `5613586` - Považská Bystrica
- `5613560` - Kysak
- `5613530` - Prešov

## API Endpoints

The library uses the following ZSSK API endpoints:
- `/api/v4/station/name/{name}` - Search stations by name
- `/api/v4/station/in-radius` - Find stations within radius
- `/api/v4/route` - Get routes between stations
- `/api/v4/route/next` - Get next route information
- `/api/v4/route/previous` - Get previous route information
- `/api/v4/train/delay` - Get train delay information

## License

This project is for educational purposes. The ZSSK API is used in accordance with its terms of service.