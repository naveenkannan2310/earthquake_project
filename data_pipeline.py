import re
from datetime import datetime, timedelta
import pandas as pd
import requests
from sqlalchemy import create_engine


def fetch_usgs_earthquake_data(years=5):
  print("Fetching earthquake data from USGS API...")
  end_date = datetime.utcnow()
  start_date = end_date - timedelta(days=365 * years)

  url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
  params = {
      "format": "geojson",
      "starttime": start_date.strftime("%Y-%m-%d"),
      "endtime": end_date.strftime("%Y-%m-%d"),
      "minmagnitude": 2.5,
  }

  response = requests.get(url, params=params)
  if response.status_code != 200:
    raise Exception(f"API Error: Status code {response.status_code}")

  data = response.json()
  features = data.get("features", [])

  records = []
  for feature in features:
    props = feature.get("properties", {})
    geom = feature.get("geometry", {})
    coords = geom.get("coordinates", [None, None, None])

    record = {
        "id": feature.get("id"),
        "time": props.get("time"),
        "updated": props.get("updated"),
        "longitude": coords[0],
        "latitude": coords[1],
        "depth_km": coords[2],
        "mag": props.get("mag"),
        "magType": props.get("magType"),
        "place": props.get("place"),
        "status": props.get("status"),
        "tsunami": props.get("tsunami"),
        "sig": props.get("sig"),
        "net": props.get("net"),
        "nst": props.get("nst"),
        "dmin": props.get("dmin"),
        "rms": props.get("rms"),
        "gap": props.get("gap"),
        "magError": props.get("magError"),
        "depthError": props.get("depthError"),
        "magNst": props.get("magNst"),
        "locationSource": props.get("locationSource"),
        "magSource": props.get("magSource"),
        "types": props.get("types"),
        "ids": props.get("ids"),
        "sources": props.get("sources"),
        "type": props.get("type"),
    }
    records.append(record)

  return pd.DataFrame(records)


def preprocess_data(df):
  print("Preprocessing data...")
  df["time"] = pd.to_datetime(df["time"], unit="ms", errors="coerce")
  df["updated"] = pd.to_datetime(df["updated"], unit="ms", errors="coerce")

  def extract_country(place):
    if pd.isna(place):
      return "Unknown"
    parts = place.split(",")
    return parts[-1].strip() if len(parts) > 1 else place.strip()

  df["country"] = df["place"].apply(extract_country)
  df["status"] = df["status"].str.lower().fillna("unknown")
  df["magType"] = df["magType"].str.lower().fillna("unknown")
  df["net"] = df["net"].str.lower().fillna("unknown")
  df["type"] = df["type"].str.lower().fillna("earthquake")

  numeric_cols = [
      "mag",
      "depth_km",
      "nst",
      "dmin",
      "rms",
      "gap",
      "magError",
      "depthError",
      "magNst",
      "sig",
  ]
  for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")
    df[col] = df[col].fillna(df[col].median() if not df[col].isna().all() else 0)

  df["tsunami"] = pd.to_numeric(df["tsunami"], errors="coerce").fillna(0).astype(int)

  df["year"] = df["time"].dt.year
  df["month"] = df["time"].dt.month
  df["day"] = df["time"].dt.day
  df["day_of_week"] = df["time"].dt.day_name()
  df["hour"] = df["time"].dt.hour
  df["depth_category"] = df["depth_km"].apply(
      lambda x: "Shallow" if x < 50 else "Deep"
  )
  return df


if __name__ == "__main__":
  df_raw = fetch_usgs_earthquake_data(years=5)
  df_clean = preprocess_data(df_raw)
  print(f"Data ready! Total records processed: {len(df_clean)}")
  # If you have MySQL installed, you can save it. Otherwise, this DataFrame handles your core processing.