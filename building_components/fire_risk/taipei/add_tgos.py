import requests
import pandas as pd
import time
import urllib.parse
import json
import re

# --------------------------------------------------
# 1. 讀取 taipei.csv（假設裡面有「地址」這個欄位）
# --------------------------------------------------
# 請確認 taipei.csv 放在此程式同一個資料夾底下
df = pd.read_csv("taipei.csv", encoding="utf-8")

# --------------------------------------------------
# 2. 定義 TGOS API 的 base URL
# --------------------------------------------------
# 注意：以下 keystr、jsonp 必須跟 TGOS 官方範例一模一樣
TGOS_BASE_URL = (
    "https://gis.tgos.tw/TGAddress/TGAddress.aspx"
    "?oSRS=EPSG:4326"
    "&oResultDataType=jsonp"
    "&pnum=NaN"
    "&keystr=QIteA7ads9%2BMjZLE5vgOm%2BS9qkcXe%2BgszjD64CBeqbA%3D"
    "&jsonp=TGOS.getJSON%5B%27sn2%27%5D"
)

def geocode_tgos(address: str):
    """
    呼叫 TGOS 地址轉座標 API，並回傳 (latitude, longitude)。
    因為 TGOS 回傳的 JSONP 內部已經是合法 JSON，所以只要把 JSONP 的包裹去掉，
    再交給 json.loads() 解析即可。若無法取得座標，就回傳 (None, None)。
    """
    # 1. URL-encode address，注意使用 quote_plus 會把空格變成 +
    addr_enc = urllib.parse.quote_plus(address)
    # 2. 組出完整的 API URL
    url = f"{TGOS_BASE_URL}&oAddress={addr_enc}"

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        text = r.text.strip()
    except Exception as e:
        print(f"  → 無法取得「{address}」的 TGOS 回應：{e}")
        return None, None

    # 3. 用 regex 把 JSONP 的包裹去掉，只留下 {...}
    #    TGOS.getJSON['sn2']({ ... });
    m = re.search(r"TGOS\.getJSON\['sn2'\]\s*\(\s*(\{.*\})\s*\)\s*;?$", text, flags=re.DOTALL)
    if not m:
        # 如果沒有 match 成功，表示回傳內容不符合預期
        print(f"  → 解析 JSONP 失敗，回傳內容（前 100 字）：\n{text[:100]}...\n")
        return None, None

    json_str = m.group(1)

    # 4. 直接用 json.loads 解析
    try:
        data = json.loads(json_str)
    except Exception as e:
        print(f"  → JSON 解析失敗：{e}")
        return None, None

    # 5. 從 data 裡取出 AddressList[0].X => lng, AddressList[0].Y => lat
    #    如果 AddressList 為空，就回 (None, None)
    addr_list = data.get("AddressList", [])
    if not addr_list:
        return None, None

    first = addr_list[0]
    lng = first.get("X")
    lat = first.get("Y")
    if lat is None or lng is None:
        return None, None

    return lat, lng

# --------------------------------------------
# 3. 在 DataFrame 裡新增 latitude、longitude 欄位
# --------------------------------------------
df["latitude"] = None
df["longitude"] = None

total = len(df)
for idx, row in df.iterrows():
    raw_addr = row["地址"]
    print(f"處理第 {idx+1}/{total} 筆：{raw_addr}")

    lat, lng = geocode_tgos(raw_addr)
    df.at[idx, "latitude"] = lat
    df.at[idx, "longitude"] = lng

    print(f"  -> lat: {lat} , lng: {lng}")
    time.sleep(0.1)  # 暫停 0.5 秒，避免呼叫過快

# --------------------------------------------
# 4. 存成新的 CSV
# --------------------------------------------
output_file = "taipei_with_latlng.csv"
df.to_csv(output_file, index=False, encoding="utf-8-sig")
print(f"所有筆地址處理完畢，檔案已儲存為：{output_file}")
