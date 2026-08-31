"""
Enhanced version of postgis_import.py with better error reporting
"""
import os

import geopandas as gpd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
import traceback

try:
    print("Step 1: Reading GeoJSON...")
    geojson_path = "gis/geojson/land.geojson"
    gdf = gpd.read_file(geojson_path)
    print(f"✓ GeoJSON loaded: {len(gdf)} records")
    print(f"  Columns: {list(gdf.columns)}")
    print(f"  CRS: {gdf.crs}")
    
    print("\nStep 2: Creating PostgreSQL engine...")
    password = os.getenv("POSTGRES_PASSWORD")
    
    # Show connection details (without exposing actual password)
    print(f"  Host: localhost")
    print(f"  Port: 2528")
    print(f"  User: postgres")
    print(f"  Database: agrie_state")
    print(f"  Password: {'*' * len(password)}")
    
    engine = create_engine(
        f"postgresql+psycopg2://postgres:{quote_plus(password)}@localhost:2528/agrie_state"
    )
    print("✓ Engine created")
    
    print("\nStep 3: Testing connection...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        print(f"✓ Connected to PostgreSQL: {version[:50]}...")
    
    print("\nStep 4: Importing data into PostGIS table 'land'...")
    gdf.to_postgis(
        "land",
        engine,
        if_exists="append",
        index=False
    )
    
    print("✓ Land data imported successfully into PostGIS!")
    print(f"  Number of records imported: {len(gdf)}")

except Exception as e:
    print(f"\n✗ ERROR: {type(e).__name__}")
    print(f"  Message: {str(e)}")
    print("\nFull traceback:")
    traceback.print_exc()
