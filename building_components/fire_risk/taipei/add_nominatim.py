import requests
import pandas as pd
import time
import urllib.parse

# ---------------------------------------------
# 1. 讀取 taipei.csv（假設裡面有「地址」這個欄位）
# ---------------------------------------------
df = pd.read_csv("taipei.csv", encoding="utf-8")

# ---------------------------------------------
# 2. 定義 Nominatim API 的 base URL 和 headers
# ---------------------------------------------
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {
    "User-Agent": "TaipeiGeocodeScript/1.0 (your_email@example.com)"  # 請改成你的 email 或識別資訊
}

def geocode_nominatim(address: str):
    """
    呼叫 Nominatim API，並回傳 (latitude, longitude)。
    如果無法取得座標或回傳列表為空，則回傳 (None, None)。
    """
    params = {
        "q": address,
        "format": "json"
    }
    try:
        response = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        results = response.json()
    except Exception as e:
        print(f"  → 無法取得「{address}」的 Nominatim 回應：{e}")
        return None, None

    if not isinstance(results, list) or len(results) == 0:
        return None, None

    first = results[0]
    lat = first.get("lat")
    lon = first.get("lon")
    # lat, lon 回傳為字串，轉成 float；若不存在就回 None
    try:
        lat = float(lat)
        lon = float(lon)
    except:
        return None, None

    return lat, lon

# --------------------------------------------
# 3. 在 DataFrame 裡新增 latitude、longitude 欄位
# --------------------------------------------
df["latitude"] = None
df["longitude"] = None

total = len(df)
for idx, row in df.iterrows():
    raw_addr = row["地址"]
    print(f"處理第 {idx+1}/{total} 筆：{raw_addr}")

    lat, lon = geocode_nominatim(raw_addr)
    df.at[idx, "latitude"] = lat
    df.at[idx, "longitude"] = lon

    print(f"  -> latitude: {lat} , longitude: {lon}")
    time.sleep(0.5)  # 暫停 1 秒，遵守 Nominatim 使用政策

# --------------------------------------------
# 4. 存成新的 CSV
# --------------------------------------------
output_file = "taipei_with_latlng.csv"
df.to_csv(output_file, index=False, encoding="utf-8-sig")
print(f"所有筆地址處理完畢，檔案已儲存為：{output_file}")
