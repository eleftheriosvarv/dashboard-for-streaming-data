from datetime import datetime, timedelta
import pytz
import os
import pandas as pd
from sqlalchemy import create_engine
import socket
import requests

def is_connected():
    try:
        socket.create_connection(("8.8.8.8", 53))
        return True
    except OSError:
        return False

def fetch_driving_travel_time(start_lat, start_lon, end_lat, end_lon, api_key):
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "routes.legs.duration"
    }
    body = {
        "origin": {"location": {"latLng": {"latitude": start_lat, "longitude": start_lon}}},
        "destination": {"location": {"latLng": {"latitude": end_lat, "longitude": end_lon}}},
        "travelMode": "DRIVE",
        "routingPreference": "TRAFFIC_AWARE"
    }
    response = requests.post(url, headers=headers, json=body)
    data = response.json()
    if "routes" in data and data["routes"]:
        duration = data["routes"][0]["legs"][0].get("duration", "0s")
        return int(duration.replace("s", "")) // 60
    return None


def fetch_transit_travel_time(start_lat, start_lon, end_lat, end_lon, api_key):
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "routes.legs.duration"
    }
    body = {
        "origin": {"location": {"latLng": {"latitude": start_lat, "longitude": start_lon}}},
        "destination": {"location": {"latLng": {"latitude": end_lat, "longitude": end_lon}}},
        "travelMode": "TRANSIT"
    }
    response = requests.post(url, headers=headers, json=body)
    data = response.json()
    if "routes" in data and data["routes"]:
        duration = data["routes"][0]["legs"][0].get("duration", "0s")
        return int(duration.replace("s", "")) // 60
    return None


def fetch_aqi(lat, lon, api_key):
    url = f"https://airquality.googleapis.com/v1/currentConditions:lookup?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "location": {"latitude": lat, "longitude": lon},
        "universalAqi": True,
        "extraComputations": ["HEALTH_RECOMMENDATIONS"],
        "languageCode": "en"
    }
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    if "indexes" in data and data["indexes"]:
        return data["indexes"][0].get("aqi", None)
    return None
def main():
    now_athens = datetime.now(pytz.utc).astimezone(pytz.timezone("Europe/Athens"))
    if not is_connected():
        print({"error": "No internet connection"})
        return

    API_KEY = os.getenv("API_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")


    engine = create_engine(DATABASE_URL)

    routes = pd.read_csv("athens_routes.csv")


    query = '''
        SELECT route_id, driving_travel_time, timestamp
        FROM travel_updates
        WHERE timestamp > NOW() - INTERVAL '3 hours'
        ORDER BY timestamp DESC
    '''
    df_history = pd.read_sql(query, con=engine)

    entropy_list = []
    for route_id in df_history["route_id"].unique():
        route_hist = df_history[df_history["route_id"] == route_id].sort_values("timestamp").head(5)
        if len(route_hist) >= 5:
            diffs = route_hist["driving_travel_time"].diff().dropna().abs()
            avg_change = diffs.mean()
            avg_time = route_hist["driving_travel_time"].mean()
            change_percent = (avg_change / avg_time) * 100 if avg_time else 100
            entropy_list.append(change_percent)

    stable_routes = [e for e in entropy_list if e < 10]
    stability_ratio = len(stable_routes) / len(entropy_list) if entropy_list else 1

    latest_ts_query = """
        SELECT timestamp
        FROM travel_updates
        ORDER BY timestamp DESC
        LIMIT 1
    """
    latest_row = pd.read_sql(latest_ts_query, con=engine)
    if not latest_row.empty:
        last_ts = latest_row.iloc[0]["timestamp"]
        last_ts = pd.to_datetime(last_ts).tz_localize("Europe/Athens")
        diff_minutes = (now_athens - last_ts).total_seconds() / 60
    else:
        diff_minutes = 9999

    should_run = False
    if stability_ratio <= 0.5:
        should_run = True
    elif stability_ratio <= 0.8 and diff_minutes > 25:
        should_run = True
    elif stability_ratio <= 1.0 and diff_minutes > 45:
        should_run = True

    if not should_run:
        print({
            "status": "skipped",
            "stability_ratio": stability_ratio,
            "last_record_minutes_ago": round(diff_minutes, 2)
        })
        return

    routes = pd.read_csv("athens_routes.csv")

    for index, row in routes.iterrows():
        driving_travel_time = fetch_driving_travel_time(
            row["start_latitude"], row["start_longitude"],
            row["end_latitude"], row["end_longitude"],
            API_KEY
        )
        routes.at[index, "driving_travel_time"] = driving_travel_time

        transit_travel_time = fetch_transit_travel_time(
            row["start_latitude"], row["start_longitude"],
            row["end_latitude"], row["end_longitude"],
            API_KEY
        )
        routes.at[index, "transit_travel_time"] = transit_travel_time

        aqi = fetch_aqi(row["start_latitude"], row["start_longitude"], API_KEY)
        routes.at[index, "aqi"] = aqi

    routes["travel_time_difference"] = routes["driving_travel_time"] - routes["transit_travel_time"]
    routes["delay_ratio"] = (
        (routes["driving_travel_time"] - routes["free_flow_driving_travel_time"]) /
        routes["free_flow_driving_travel_time"]
    ).round(2)

    routes.to_sql("travel_updates", con=engine, if_exists="append", index=False)


    print({
        "status": "updated",
        "stability_ratio": stability_ratio,
        "records_added": len(routes),
        "last_record_minutes_ago": round(diff_minutes, 2)
    })

if __name__ == "__main__":
    main()
