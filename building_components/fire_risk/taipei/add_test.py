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
    raw_addr = row["地址"]
    # 如果地址包含「號」，只取第一個「號」之前(含「號」)去查詢
    if "號" in raw_addr:
        pos = raw_addr.find("號")
        query_addr = raw_addr[: pos + 1]
    else:
        query_addr = raw_addr

    # 印出目前進度
    print(f"處理第 {idx+1}/{total} 筆地址：{raw_addr}  → 查詢：{query_addr}")

    lat, lng = geocode_arcgis(query_addr)
    df.at[idx, "latitude"] = lat
    df.at[idx, "longitude"] = lng

    # 印出取得的經緯度
    print(f"  -> latitude: {lat}  longitude: {lng}")

    time.sleep(0.05)  # 暫停 0.5 秒，避免連續呼叫過快

# 4. 將結果存成新的 CSV
output_file = "taipei_latlng_ver2.csv"
df.to_csv(output_file, index=False, encoding="utf-8-sig")

print(f"已完成經緯度填寫，結果已儲存到 {output_file}")
