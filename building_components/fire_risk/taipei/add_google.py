import requests
import pandas as pd
import time
import urllib.parse
import re
import json

# ---------------------------------------------
# 1. 讀取 taipei.csv（請放在與此程式同一資料夾，且有「地址」欄位）
# ---------------------------------------------
df = pd.read_csv("taipei.csv", encoding="utf-8")

# ---------------------------------------------
# 2. 定義 Google Maps URL 與 headers（一定要帶 User-Agent）
# ---------------------------------------------
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/90.0.4430.93 Safari/537.36"
    )
}

# ---------------------------------------------
# 3. 行政區清單
# ---------------------------------------------
districts = [
    "北投區", "士林區", "內湖區", "南港區", "松山區", "信義區", "中山區", "大同區",
    "中正區", "萬華區", "大安區", "文山區", "新莊區", "淡水區", "汐止區", "板橋區",
    "三重區", "樹林區", "土城區", "蘆洲區", "中和區", "永和區", "新店區", "鶯歌區",
    "三峽區", "瑞芳區", "五股區", "泰山區", "林口區", "深坑區", "石碇區", "坪林區",
    "三芝區", "石門區", "八里區", "平溪區", "雙溪區", "貢寮區", "金山區", "萬里區",
    "烏來區"
]

def fetch_raw_app_state(address: str):
    """
    呼叫 Google Maps place 網頁，手動「找 bracket 深度」截出
    window.APP_INITIALIZATION_STATE 裡的 JSON 字串，並回傳 HTML。
    回傳 (raw_json, html_text)，若失敗則 (None, None)。
    """
    addr_enc = urllib.parse.quote_plus(address)
    url = f"https://www.google.com/maps/place?q={addr_enc}"
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        text = res.text
    except Exception as e:
        print(f"  → 無法取得「{address}」的 Google Maps 回應：{e}")
        return None, None

    marker = "window.APP_INITIALIZATION_STATE="
    idx = text.find(marker)
    if idx == -1:
        print(f"  → 找不到 'window.APP_INITIALIZATION_STATE' 標記，跳過「{address}」")
        return None, text

    start = text.find("[", idx)
    if start == -1:
        print(f"  → 找不到 '['，無法定位 JSON 區段，跳過「{address}」")
        return None, text

    depth = 0
    end = -1
    for i in range(start, len(text)):
        if text[i] == "[":
            depth += 1
        elif text[i] == "]":
            depth -= 1
        if depth == 0:
            end = i
            break

    if end == -1:
        print(f"  → 無法找到對應的 ']'，JSON 可能不完整，跳過「{address}」")
        return None, text

    raw_json = text[start : end + 1]
    return raw_json, text

def parse_xy_from_rawjson(raw_json: str):
    """
    用字串方法，找到 raw_json 中第一個 ']' 前，往前兩個逗號，解析 x, y。
    回傳 (latitude, longitude)，若無法解析回 (None, None)。
    """
    first_end = raw_json.find("]")
    if first_end == -1:
        return None, None

    substring = raw_json[:first_end]
    comma1 = substring.rfind(",")
    if comma1 == -1:
        return None, None
    comma2 = substring.rfind(",", 0, comma1)
    if comma2 == -1:
        return None, None

    x_str = substring[comma2 + 1: comma1].strip()
    y_str = substring[comma1 + 1:].strip()

    try:
        lon = float(x_str)
        lat = float(y_str)
    except ValueError:
        return None, None

    return lat, lon

# --------------------------------------------
# 4. 在 DataFrame 裡新增 latitude、longitude、行政區 欄位
# --------------------------------------------
df["latitude"] = None
df["longitude"] = None
df["行政區"] = None

total = len(df)
for idx, row in df.iterrows():
    raw_addr = row["地址"]
    print(f"\n處理第 {idx+1}/{total} 筆：{raw_addr}")

    raw_json, html_text = fetch_raw_app_state(raw_addr)
    if raw_json is None:
        print("  -> 無法取得 raw_json，跳過 XY 解析")
    else:
        print("  -> 抓到的 raw_json（前 150 字）：")
        print(raw_json[:150] + " ...")
        lat, lon = parse_xy_from_rawjson(raw_json)
        df.at[idx, "latitude"] = lat
        df.at[idx, "longitude"] = lon
        print(f"  -> 解析後 latitude: {lat} , longitude: {lon}")

    # 解析行政區：在 html_text 中循序搜尋區名
    found_district = None
    if html_text:
        for dist in districts:
            if dist in html_text:
                found_district = dist
                break
    df.at[idx, "行政區"] = found_district
    print(f"  -> 辨識行政區: {found_district}")

    time.sleep(1)  # 建議等 1 秒，避免被 Google 臨時封鎖

# --------------------------------------------
# 5. 存成新的 CSV
# --------------------------------------------
output_file = "retry.csv"
df.to_csv(output_file, index=False, encoding="utf-8-sig")
print(f"\n所有筆地址處理完畢，檔案已儲存為：{output_file}")
