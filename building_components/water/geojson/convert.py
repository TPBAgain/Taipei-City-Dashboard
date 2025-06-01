import pandas as pd
import json

def csv_to_geojson(input_csv, output_geojson):
    df = pd.read_csv(input_csv)
    features = []
    # 每個點對應一個小方形
    size = 0.005  # 調整邊長
    for _, row in df.iterrows():
        lon = row['Longitude']
        lat = row['Latitude']
        h   = row['淹水時間(分鐘)']
        name = row['位置']
        district = row['行政區']
        half = size / 2
        # 四邊坐標 (順時針)
        coords = [
            [lon - half, lat - half],
            [lon + half, lat - half],
            [lon + half, lat + half],
            [lon - half, lat + half],
            [lon - half, lat - half]
        ]
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [coords]
            },
            "properties": {
                "name": name,
                "district": district,
                "height": h,
                "base_height": 0
            }
        }
        features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    with open(output_geojson, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    csv_to_geojson("tpe_with_POS.csv", "flood_tpe.geojson")
    print("已生成geojson")
