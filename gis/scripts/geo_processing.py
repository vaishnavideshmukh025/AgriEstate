import geopandas as gpd

# Read our existing GeoJSON file
geojson_path = "../geojson/land.geojson"

gdf = gpd.read_file(geojson_path)

print("Total land records:", len(gdf))

print("\nLand Data:")
print(gdf)

print("\nColumns:")
print(gdf.columns)

print("\nCoordinate Reference System:")
print(gdf.crs)

# Find vacant and underutilized land
candidate_land = gdf[
    gdf["current_usage"].isin(["Vacant", "Underutilized"])
]

print("\nCandidate Land:")
print(candidate_land[
    ["land_id", "name", "land_type", "current_usage", "area_sqft"]
])

print("\nNumber of candidate sites:", len(candidate_land))

# Apply basic suitability conditions
suitable_land = candidate_land[
    (candidate_land["area_sqft"] >= 4000) &
    (candidate_land["sunlight_hours"] >= 7) &
    (candidate_land["water_access"].isin(["High", "Medium"]))
]

print("\nSuitable Land:")
print(suitable_land[
    [
        "land_id",
        "name",
        "land_type",
        "current_usage",
        "area_sqft",
        "sunlight_hours",
        "water_access"
    ]
])

print("\nNumber of suitable sites:", len(suitable_land))