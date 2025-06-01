import requests
import pandas as pd
import time

# 1. 讀取 taipei.csv，其中假設「地址」是欄位名稱
df = pd.read_csv("taipei.csv", encoding="utf-8")

# 2. ArcGIS Geocode API 的 endpoint
GEOCODE_URL = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates"

def geocode_arcgis(single_line):
    """
    呼叫 ArcGIS World Geocode Server 的 findAddressCandidates，
    回傳第一筆候選地址的 (latitude, longitude)。若找不到則回傳 (None, None)。
    """
    params = {
        "SingleLine": single_line,
        "f": "json",
        "outSR": '{"wkid":4326}',         
        "outFields": "Addr_type,Match_addr,StAddr,City",
        "maxLocations": 1                 
    }
    try:
        res = requests.get(GEOCODE_URL, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        print(f"無法取得「{single_line}」的 Geocode 資訊：{e}")
        return None, None

    candidates = data.get("candidates", [])
    if not candidates:
        return None, None

    first = candidates[0]
    loc = first.get("location", {})
    longitude = loc.get("x")  # 經度
    latitude = loc.get("y")   # 緯度
    return latitude, longitude

# 3. 在 DataFrame 中新增 latitude、longitude 欄位
df["latitude"] = None
df["longitude"] = None

total = len(df)
for idx, row in df.iterrows():
    address = row["地址"]
    # 印出目前進度
    print(f"處理第 {idx+1}/{total} 筆地址：{address}")

    lat, lng = geocode_arcgis(address)
    df.at[idx, "latitude"] = lat
    df.at[idx, "longitude"] = lng

    # 可選：印出取得的經緯度（找不到時會是 None）
    print(f"  -> latitude: {lat}  longitude: {lng}")

    time.sleep(0.5)  # 暫停 0.5 秒，避免連續呼叫過快

# 4. 將結果存成新的 CSV
output_file = "taipei_latlng.csv"
df.to_csv(output_file, index=False, encoding="utf-8-sig")

print(f"已完成經緯度填寫，結果已儲存到 {output_file}")
