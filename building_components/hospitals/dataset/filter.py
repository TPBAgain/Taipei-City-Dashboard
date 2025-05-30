import os
import pandas as pd

# 1. 讀取 city_code.csv，找出台北市的 code
city_codes = pd.read_csv('city_code.csv', dtype=str)  # 欄位：code, name
taipei_code = city_codes.loc[
    city_codes['name'].str.contains('新北市'), 'code'
].iloc[0]

# 2. 設定輸入／輸出目錄（同級，就是 dataset/ 底下）
input_dir = '.'  # filter.py 所在路徑
output_dir = 'filtered_New_Taipei'
os.makedirs(output_dir, exist_ok=True)

# 3. 要篩選的檔案清單（皆在同一層）
files = [
    'clinic.csv',
    'district_hospital.csv',
    'regional_hospital.csv',
    'medical_center.csv'
]

for fname in files:
    in_path = os.path.join(input_dir, fname)
    df = pd.read_csv(in_path, dtype=str)
    # 篩選「縣市別代碼」等於台北市代碼
    filtered = df[df['縣市別代碼'] == taipei_code]
    # 輸出到 dataset/filtered_Taipei/，檔名相同
    out_path = os.path.join(output_dir, fname)
    filtered.to_csv(out_path, index=False, encoding='utf-8-sig')
    print(f'Filtered {fname}: {len(filtered)} rows → {out_path}')
