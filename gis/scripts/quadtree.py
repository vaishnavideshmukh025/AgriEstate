import geopandas as gpd


# -----------------------------
# Quadtree Node
# -----------------------------

class QuadTree:
    def __init__(self, min_x, min_y, max_x, max_y, capacity=2):
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y

        self.capacity = capacity
        self.points = []

        self.divided = False

        self.north_west = None
        self.north_east = None
        self.south_west = None
        self.south_east = None

    # Check whether a point belongs to this region
    def contains(self, x, y):
        return (
            self.min_x <= x <= self.max_x
            and self.min_y <= y <= self.max_y
        )

    # Divide the region into four parts
    def subdivide(self):

        center_x = (self.min_x + self.max_x) / 2
        center_y = (self.min_y + self.max_y) / 2

        self.north_west = QuadTree(
            self.min_x,
            center_y,
            center_x,
            self.max_y,
            self.capacity
        )

        self.north_east = QuadTree(
            center_x,
            center_y,
            self.max_x,
            self.max_y,
            self.capacity
        )

        self.south_west = QuadTree(
            self.min_x,
            self.min_y,
            center_x,
            center_y,
            self.capacity
        )

        self.south_east = QuadTree(
            center_x,
            self.min_y,
            self.max_x,
            center_y,
            self.capacity
        )

        self.divided = True

    # Insert a land point
    def insert(self, point):

        x = point["x"]
        y = point["y"]

        if not self.contains(x, y):
            return False

        # If there is space in this region
        if len(self.points) < self.capacity and not self.divided:
            self.points.append(point)
            return True

        # If region is full, divide it
        if not self.divided:
            self.subdivide()

            # Move existing points into child regions
            existing_points = self.points
            self.points = []

            for existing_point in existing_points:
                self.insert(existing_point)

        # Insert new point into appropriate region
        if self.north_west.insert(point):
            return True

        if self.north_east.insert(point):
            return True

        if self.south_west.insert(point):
            return True

        if self.south_east.insert(point):
            return True

        return False


# -----------------------------
# Read GeoJSON
# -----------------------------

geojson_path = "../geojson/land.geojson"

gdf = gpd.read_file(geojson_path)


# -----------------------------
# Filter suitable land
# -----------------------------

suitable_land = gdf[
    (gdf["current_usage"].isin(["Vacant", "Underutilized"])) &
    (gdf["area_sqft"] >= 4000) &
    (gdf["sunlight_hours"] >= 7) &
    (gdf["water_access"].isin(["High", "Medium"]))
].copy()

print("Number of suitable sites:", len(suitable_land))


# -----------------------------
# Prepare points
# -----------------------------

points = []

for position, geometry in enumerate(suitable_land.geometry):

    points.append({
        "land_id": suitable_land.iloc[position]["land_id"],
        "x": geometry.x,
        "y": geometry.y
    })


# -----------------------------
# Create Quadtree
# -----------------------------

min_x, min_y, max_x, max_y = suitable_land.total_bounds

quadtree = QuadTree(
    min_x,
    min_y,
    max_x,
    max_y,
    capacity=2
)


# -----------------------------
# Insert all land points
# -----------------------------

for point in points:
    quadtree.insert(point)


print("Recursive Quadtree created successfully!")
print("Maximum points per region: 2")

# -----------------------------
# Search Quadtree
# -----------------------------

def search(node, min_x, min_y, max_x, max_y, results):
    """
    Find land points inside the given search area.
    """

    # If the search area does not overlap this node, stop
    if (
        node.max_x < min_x or
        node.min_x > max_x or
        node.max_y < min_y or
        node.min_y > max_y
    ):
        return

    # Check points stored in this node
    for point in node.points:
        if (
            min_x <= point["x"] <= max_x and
            min_y <= point["y"] <= max_y
        ):
            results.append(point["land_id"])

    # Search child regions
    if node.divided:
        search(node.north_west, min_x, min_y, max_x, max_y, results)
        search(node.north_east, min_x, min_y, max_x, max_y, results)
        search(node.south_west, min_x, min_y, max_x, max_y, results)
        search(node.south_east, min_x, min_y, max_x, max_y, results)


# -----------------------------
# Example spatial search
# -----------------------------

# Create a search area around the center
center_x = (min_x + max_x) / 2
center_y = (min_y + max_y) / 2

search_results = []

search(
    quadtree,
    center_x - 0.003,
    center_y - 0.003,
    center_x + 0.003,
    center_y + 0.003,
    search_results
)

print("\nQuadtree Search Results:")

if search_results:
    for land_id in search_results:
        print(land_id)
else:
    print("No suitable land found.")