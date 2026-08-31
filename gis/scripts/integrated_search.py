import geopandas as gpd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

print("=" * 70)
print("AGRI-ESTATE INTEGRATED SPATIAL SEARCH")
print("=" * 70)

# ---------------------------------------------------------
# 1. Load land data
# ---------------------------------------------------------

geojson_path = "../geojson/land.geojson"

gdf = gpd.read_file(geojson_path)

print(f"\nTotal land records: {len(gdf)}")
print("Land data loaded successfully.")

# ---------------------------------------------------------
# 2. R-Tree Spatial Search
# ---------------------------------------------------------

print("\n" + "-" * 70)
print("STEP 1: R-TREE SEARCH")
print("-" * 70)

# Create spatial index
spatial_index = gdf.sindex

print("R-Tree index created successfully!")

# Study area
min_x = 73.000
min_y = 18.000
max_x = 73.004
max_y = 18.008

# Search using bounding box
possible_matches = list(
    spatial_index.intersection(
        (min_x, min_y, max_x, max_y)
    )
)

rtree_results = gdf.iloc[possible_matches]

print(f"R-Tree candidates found: {len(rtree_results)}")

for _, row in rtree_results.iterrows():
    print(f"{row['land_id']} - {row['name']}")

# ---------------------------------------------------------
# 3. Quadtree Spatial Search
# ---------------------------------------------------------

print("\n" + "-" * 70)
print("STEP 2: QUADTREE SEARCH")
print("-" * 70)

# Calculate center of study area
center_x = (min_x + max_x) / 2
center_y = (min_y + max_y) / 2

print(f"Study Area Center: ({center_x}, {center_y})")

# Divide R-Tree results into four regions
quadtree_results = {
    "North-West": [],
    "North-East": [],
    "South-West": [],
    "South-East": []
}

for _, row in rtree_results.iterrows():

    x = row.geometry.x
    y = row.geometry.y

    if x <= center_x and y >= center_y:
        quadtree_results["North-West"].append(row["land_id"])

    elif x > center_x and y >= center_y:
        quadtree_results["North-East"].append(row["land_id"])

    elif x <= center_x and y < center_y:
        quadtree_results["South-West"].append(row["land_id"])

    else:
        quadtree_results["South-East"].append(row["land_id"])


print("\nQuadtree Regions:")

for region, lands in quadtree_results.items():
    print(f"{region}: {lands}")    

# ---------------------------------------------------------
# 4. PostGIS Spatial Search
# ---------------------------------------------------------

print("\n" + "-" * 70)
print("STEP 3: POSTGIS SEARCH")
print("-" * 70)

import os
password = os.getenv("POSTGRES_PASSWORD")


# Create database connection
engine = create_engine(
    f"postgresql+psycopg2://postgres:{quote_plus(password)}@localhost:2528/agrie_state"
)

print("Connecting to PostGIS...")

with engine.connect() as conn:

    # Check PostGIS version
    result = conn.execute(
        text("SELECT PostGIS_Version();")
    )

    postgis_version = result.fetchone()[0]

    print(f"PostGIS connected successfully!")
    print(f"PostGIS version: {postgis_version}")

    # Count land records
    result = conn.execute(
        text("SELECT COUNT(*) FROM land;")
    )

    total_records = result.fetchone()[0]

    print(f"Records in PostGIS: {total_records}")

# ---------------------------------------------------------
# 5. Final Suitability Filtering
# ---------------------------------------------------------

print("\n" + "-" * 70)
print("STEP 4: FINAL SUITABILITY FILTERING")
print("-" * 70)

query = text("""
    SELECT land_id, name, area_sqft,
           sunlight_hours, water_access,
           market_distance_km
    FROM land
    WHERE area_sqft >= 4000
      AND sunlight_hours >= 7
      AND water_access IN ('High', 'Medium')
      AND market_distance_km <= 5
    ORDER BY land_id;
""")

with engine.connect() as conn:

    result = conn.execute(query)

    rows = result.fetchall()

    print(f"\nFinal suitable sites: {len(rows)}")

    print("\nSuitable Land Results:")

    for row in rows:
        print(
            f"{row.land_id} - {row.name} | "
            f"Area: {row.area_sqft} sqft | "
            f"Sunlight: {row.sunlight_hours} hrs | "
            f"Water: {row.water_access} | "
            f"Market: {row.market_distance_km} km"
        )

print("\n" + "=" * 70)
print("INTEGRATED SPATIAL SEARCH COMPLETED")
print("=" * 70)    