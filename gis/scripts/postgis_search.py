import os

import geopandas as gpd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
password = os.getenv("POSTGRES_PASSWORD")

# PostgreSQL connection
engine = create_engine(
    f"postgresql+psycopg2://postgres:{quote_plus(password)}@localhost:2528/agrie_state"
)

print("=" * 60)
print("POSTGIS SPATIAL SEARCH")
print("=" * 60)

# Study area
min_x = 73.000
min_y = 18.000
max_x = 73.004
max_y = 18.008

# Spatial query
query = text("""
    SELECT
        land_id,
        name,
        land_type,
        current_usage,
        area_sqft,
        sunlight_hours,
        water_access,
        market_distance_km
    FROM land
    WHERE ST_Intersects(
        geom,
        ST_MakeEnvelope(
            :min_x, :min_y,
            :max_x, :max_y,
            4326
        )
    )
    ORDER BY land_id;
""")

with engine.connect() as conn:
    result = conn.execute(
        query,
        {
            "min_x": min_x,
            "min_y": min_y,
            "max_x": max_x,
            "max_y": max_y
        }
    )

    rows = result.fetchall()

print("\nPostGIS Spatial Search Results:")
print("-" * 60)

for row in rows:
    print(f"{row[0]} - {row[1]}")

print("-" * 60)
print(f"Number of lands found: {len(rows)}")
print("\nPostGIS spatial search completed successfully!")