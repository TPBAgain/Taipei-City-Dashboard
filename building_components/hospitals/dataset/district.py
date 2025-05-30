import os
import pandas as pd

# 1. 讀取行政區代碼表
district_codes = pd.read_csv('taipei_district_code.csv', dtype=str)

# 2. 定義資料夾
input_dir = 'filtered_Taipei'
output_dir = 'enriched_Taipei'
os.makedirs(output_dir, exist_ok=True)

# 3. 臺北市 12 區中文全名清單
taipei_districts = district_codes['行政區名稱'].tolist()

def extract_district(addr: str) -> str:
    if not isinstance(addr, str):
        return ''
    for dist in taipei_districts:
        if dist in addr:
            return dist
    return ''

# 4. 處理每一個 CSV
for fname in os.listdir(input_dir):
    if not fname.endswith('.csv'):
        continue

    df = pd.read_csv(os.path.join(input_dir, fname), dtype=str)

    # 5. 從地址提取「行政區名稱」
    df['行政區名稱'] = df['地址'].apply(extract_district)

    # 6. 合併取得「行政區編碼」
    df = df.merge(
        district_codes,
        on='行政區名稱',
        how='left'
    )

    # 7. 找出合併後「行政區編碼」為空的列索引
    null_idx = df[df['行政區編碼'].isna()].index.tolist()
    if null_idx:
        print(f'{fname} 中以下列索引沒有對應到行政區：{null_idx}')
    else:
        print(f'{fname} 全部都有對應到行政區')

    # 8. 輸出
    out_path = os.path.join(output_dir, fname)
    df.to_csv(out_path, index=False, encoding='utf-8-sig')
    print(f'Enriched {fname} → {out_path}\n')
