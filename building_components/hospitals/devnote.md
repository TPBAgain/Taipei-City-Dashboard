# Overview
This is the dev note of "醫療院所等級密度（診所、區域醫院、地方醫院、醫學中心）" under "健康照護" category.
Written by Eric on May 30, 2025.

# Data pre-processing
## datasets fetching
Since [data.taipei](https://data.taipei/dataset/detail?id=ffdd5753-30db-4c38-b65f-b77892773d60) doesn't provide the type of health facilities, so we need to find another alternative dataset.

At NHI website, I found that there are four datasets which have already devided by the type of health facilities.
- [健保特約醫事機構-診所](https://info.nhi.gov.tw/IODE0000/IODE0000S09?id=328)
  - saved as dataset/clinic.csv
- [健保特約醫事機構-地區醫院](https://info.nhi.gov.tw/IODE0000/IODE0000S09?id=327)
  - saved as dataset/district_hospital.csv
- [健保特約醫事機構-區域醫院](https://info.nhi.gov.tw/IODE0000/IODE0000S09?id=326)
  - saved as dataset/regional_hospital.csv
- [健保特約醫事機構-醫學中心](https://info.nhi.gov.tw/IODE0000/IODE0000S09?id=325)
  - saved as dataset/medical_center.csv

Now we have four csv that contains the information of health facilities.

## Fliter health facilities in Taipei city
After getting the information of health facilities, we need to fliter health facilities in Taipei city only.

In those datasets, there's a column named "縣市別代碼".

Refering [government dataset schema](https://schema.nat.gov.tw/lists/157), the meaning of this code can be found at [戶役政資訊系統資料代碼內容清單](https://www.ris.gov.tw/documents/html/5/1/168.html).
The comparision table is "縣市代碼" with a code of "RSCD0102.txt". I've saved and convert this table as dataset/city_code.csv.

Using dataset/filter.py to filter rows of health facilities in Taipei (as well as New Taipei).
After running this .py, there will be new datasets under dataset/filtered_Taipei.

## Add district information (currently done Taipei city only)
Using dataset/district.py to add district information to the dataset. I used the address column to interpret the district information. 
After running this .py, there will be new datasets under dataset/enriched_Taipei.

*Note that dataset of New Taipei city HAS NOT been added district information.*


# Build database
The docs recommends Airflow and API to automatically update data. But it also suggests that we should use pandas for testing. We don't necessarly need to apply auto-update feature in the beginning.

Thus, I created a folder pandas_testing for this version of the component (with pandas).

Using pandas/testing/count.py to calculate the density of health facilities in Taipei by districts. Save the calculation result as pandas/testing/taipei_hospital_density.csv.



