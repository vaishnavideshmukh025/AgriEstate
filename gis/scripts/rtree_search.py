import geopandas as gpd
from rtree import index
from shapely.geometry import box

# Read our land data
geojson_path = "../geojson/land.geojson"
gdf = gpd.read_file(geojson_path)

# Filter suitable land
suitable_land = gdf[
    (gdf["current_usage"].isin(["Vacant", "Underutilized"])) &
    (gdf["area_sqft"] >= 4000) &
    (gdf["sunlight_hours"] >= 7) &
    (gdf["water_access"].isin(["High", "Medium"]))
].copy()

print("Number of suitable sites:", len(suitable_land))

# Create R-Tree index
spatial_index = index.Index()

for position, geometry in enumerate(suitable_land.geometry):
    spatial_index.insert(position, geometry.bounds)

print("R-Tree index created successfully!")

# -------------------------------------------------
# Create a search area
# -------------------------------------------------

# Get the total area covered by our suitable sites
min_x, min_y, max_x, max_y = suitable_land.total_bounds

# Create a search rectangle around the middle of our dataset
center_x = (min_x + max_x) / 2
center_y = (min_y + max_y) / 2

search_area = box(
    center_x - 0.003,
    center_y - 0.003,
    center_x + 0.003,
    center_y + 0.003
)

# Search using R-Tree
results = list(
    spatial_index.intersection(search_area.bounds)
)

print("\nR-Tree Search Results:")

if results:
    for result in results:
        land = suitable_land.iloc[result]
        print(
            land["land_id"],
            "-",
            land["name"]
        )
else:
    print("No suitable land found in the search area.")