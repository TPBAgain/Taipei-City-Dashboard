import pandas as pd

# 直接讀入院所 csv
clinic = pd.read_csv('../dataset/enriched_Taipei/clinic.csv')
district_hosp = pd.read_csv('../dataset/enriched_Taipei/district_hospital.csv')
regional_hosp = pd.read_csv('../dataset/enriched_Taipei/regional_hospital.csv')
med_center = pd.read_csv('../dataset/enriched_Taipei/medical_center.csv')

# groupby「行政區名稱」並保留「行政區編碼」
def group_count(df, name):
    return df.groupby(['行政區名稱', '行政區編碼']).size().reset_index(name=name)

clinic_count = group_count(clinic, '診所')
district_count = group_count(district_hosp, '地方醫院')
regional_count = group_count(regional_hosp, '區域醫院')
center_count = group_count(med_center, '醫學中心')

# 依「行政區名稱」和「行政區編碼」合併
result = clinic_count.merge(district_count, on=['行政區名稱', '行政區編碼'], how='outer')
result = result.merge(regional_count, on=['行政區名稱', '行政區編碼'], how='outer')
result = result.merge(center_count, on=['行政區名稱', '行政區編碼'], how='outer')
result = result.fillna(0).astype({'診所': int, '地方醫院': int, '區域醫院': int, '醫學中心': int})

# 依行政區名稱排序
result = result.sort_values(by='行政區名稱').reset_index(drop=True)

print(result)
result.to_csv('taipei_hospital_density.csv', index=False)
