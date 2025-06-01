import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time

INPUT_CSV = "tpe.csv"
OUTPUT_CSV = "tpe_with_POS.csv"
DELAY_SECONDS = 1.0  # To avoid rate-limiting or blocks

def get_lat_lon_from_google_maps(address):
    """
    Send a GET request to Google Maps and parse the lat/lon from the staticmap URL in the <meta> tag.
    """
    try:
        search_url = f"https://www.google.com/maps/place?q={requests.utils.quote(address)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; ScraperBot/1.0; +http://example.com/bot)"
        }
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        meta_tag = soup.find("meta", {"itemprop": "image"})
        if meta_tag and "content" in meta_tag.attrs:
            staticmap_url = meta_tag["content"]
            # Extract the lat/lon from the staticmap URL
            match = re.search(r"center=([0-9.\-]+)%2C([0-9.\-]+)", staticmap_url)
            if match:
                lat = float(match.group(1))
                lon = float(match.group(2))
                return lat, lon
        # fallback if no match
        return None, None
    except Exception as e:
        print(f"Error processing '{address}': {e}")
        return None, None

def main():
    df = pd.read_csv(INPUT_CSV)
    df["Latitude"] = None
    df["Longitude"] = None

    for idx, row in df.iterrows():
        address = "台北市" + row["地址"]
        print(f"Processing {idx+1}/{len(df)}: {address}")
        lat, lon = get_lat_lon_from_google_maps(address)
        df.at[idx, "Latitude"] = lat
        df.at[idx, "Longitude"] = lon
        time.sleep(DELAY_SECONDS)  # Be polite to avoid getting blocked

    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Geocoding complete! Results saved to '{OUTPUT_CSV}'.")

if __name__ == "__main__":
    main()