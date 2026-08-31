import os

import geopandas as gpd
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# Read our GeoJSON
geojson_path = "gis/geojson/land.geojson"
gdf = gpd.read_file(geojson_path)

# IMPORTANT: Rename 'geometry' column to 'geom' to match existing PostGIS table
gdf = gdf.rename_geometry("geom")

password = os.getenv("POSTGRES_PASSWORD")

# PostgreSQL connection
engine = create_engine(
    f"postgresql+psycopg2://postgres:{quote_plus(password)}@localhost:2528/agrie_state"
)

# Import data into PostGIS
gdf.to_postgis(
    "land",
    engine,
    if_exists="append",
    index=False
)

print("Land data imported successfully into PostGIS!")
print("Number of records:", len(gdf))