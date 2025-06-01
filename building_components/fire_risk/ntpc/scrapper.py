import requests
from bs4 import BeautifulSoup
import time
import csv

BASE_URL = "https://www.fire.ntpc.gov.tw/PageListdata/go_page"
FID = 71
DELAY = 0.3
OUTPUT_CSV = "ntpc_fire_html.csv"

def fetch_page_html(fid: int, page: int):
    url = f"{BASE_URL}?page={page}&fid={fid}"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.text

def parse_rows_from_html(html: str):
    soup = BeautifulSoup(html, "html.parser")
    container = soup.find("div", class_=f"listdataTb listdata-{FID}")
    if not container:
        return []
    row_uls = container.find_all("ul", class_="tcont flex")
    records = []
    for ul in row_uls:
        lis = ul.find_all("li")
        if len(lis) < 5:
            continue
        idx = lis[0].find("div", class_="cont").get_text(strip=True)
        district = lis[1].find("div", class_="cont").get_text(strip=True)
        team = lis[2].find("div", class_="cont").get_text(strip=True)
        location = lis[3].find("div", class_="cont").get_text(strip=True)
        wl = lis[4].find("div", class_="cont").get_text(separator=" ", strip=True)
        # 假設寬度與長度格式是「寬度約:2.1 長度約:150」
        width = ""
        length = ""
        parts = wl.split()
        for part in parts:
            if part.startswith("寬度"):
                width = part.split(":")[-1]
            if part.startswith("長度"):
                length = part.split(":")[-1]
        records.append({
            "編號": idx,
            "行政區": district,
            "轄區分隊": team,
            "巷道地點": location,
            "寬度": width,
            "長度": length
        })
    return records

def crawl_all_pages(fid: int):
    all_records = []
    page = 1
    while True:
        try:
            html = fetch_page_html(fid, page)
        except Exception as e:
            print(f"第 {page} 頁請求失敗  停止抓取")
            break
        rows = parse_rows_from_html(html)
        if not rows:
            print(f"第 {page} 頁沒有資料  結束")
            break
        all_records.extend(rows)
        print(f"第 {page} 頁抓到 {len(rows)} 筆  累計 {len(all_records)} 筆")
        page += 1
        time.sleep(DELAY)
    return all_records

def save_to_csv(filename: str, data: list):
    if not data:
        return
    fieldnames = ["編號", "行政區", "轄區分隊", "巷道地點", "寬度", "長度"]
    with open(filename, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print(f"已寫入 {len(data)} 筆  到 {filename}")

if __name__ == "__main__":
    all_data = crawl_all_pages(FID)
    save_to_csv(OUTPUT_CSV, all_data)
