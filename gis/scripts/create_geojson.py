import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os

# 1. Read CSV file
csv_path = "../data/land_data.csv"
df = pd.read_csv(csv_path)

# 2. Create synthetic coordinates
# These coordinates are ONLY for our dummy project dataset
base_lat = 18.0000
base_lon = 73.0000

coordinates = []

for i in range(len(df)):
    lat = base_lat + (i % 5) * 0.002
    lon = base_lon + (i // 5) * 0.002
    coordinates.append(Point(lon, lat))

# 3. Create GeoDataFrame
gdf = gpd.GeoDataFrame(
    df,
    geometry=coordinates,
    crs="EPSG:4326"
)

# 4. Create output folder if it doesn't exist
output_folder = "../geojson"
os.makedirs(output_folder, exist_ok=True)

# 5. Save as GeoJSON
output_path = "../geojson/land.geojson"
gdf.to_file(output_path, driver="GeoJSON")

print("GeoJSON created successfully!")
print(f"Saved at: {output_path}")
print(f"Total land records: {len(gdf)}")