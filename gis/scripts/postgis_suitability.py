import os

from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

password = os.getenv("POSTGRES_PASSWORD")

# PostgreSQL connection
engine = create_engine(
    f"postgresql+psycopg2://postgres:{quote_plus(password)}@localhost:2528/agrie_state"
)

print("=" * 60)
print("POSTGIS SUITABILITY SEARCH")
print("=" * 60)

query = text("""
    SELECT
        land_id,
        name,
        area_sqft,
        sunlight_hours,
        water_access,
        market_distance_km
    FROM land
    WHERE
        area_sqft >= 4000
        AND sunlight_hours >= 7
        AND water_access IN ('High', 'Medium')
        AND market_distance_km <= 5
    ORDER BY land_id;
""")

with engine.connect() as conn:
    result = conn.execute(query)
    rows = result.fetchall()

print("\nSuitable Lands:")
print("-" * 60)

for row in rows:
    print(
        f"{row[0]} - {row[1]} | "
        f"Area: {row[2]} sqft | "
        f"Sunlight: {row[3]} hrs | "
        f"Water: {row[4]} | "
        f"Market: {row[5]} km"
    )

print("-" * 60)
print(f"Number of suitable lands: {len(rows)}")

print("\nPostGIS suitability search completed successfully!")