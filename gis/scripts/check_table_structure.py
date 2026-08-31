import os
from sqlalchemy import create_engine, text, inspect
from urllib.parse import quote_plus

password = os.getenv("POSTGRES_PASSWORD")
engine = create_engine(
    f"postgresql+psycopg2://postgres:{quote_plus(password)}@localhost:2528/agrie_state"
)

print("=" * 70)
print("POSTGIS TABLE STRUCTURE CHECK")
print("=" * 70)

with engine.connect() as conn:
    # Check if table exists
    print("\n[1] Checking if 'land' table exists...")
    result = conn.execute(text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'land'
        );
    """))
    table_exists = result.fetchone()[0]
    print(f"    Table exists: {table_exists}")
    
    if table_exists:
        # Get table structure
        print("\n[2] Table structure:")
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'land'
            ORDER BY ordinal_position;
        """))
        for row in result:
            nullable = "NULL" if row[2] == "YES" else "NOT NULL"
            print(f"    - {row[0]:<20} {row[1]:<20} {nullable}")
        
        # Check for geometry column
        print("\n[3] PostGIS geometry columns:")
        result = conn.execute(text("""
            SELECT f_table_name, f_geometry_column, type, srid
            FROM geometry_columns
            WHERE f_table_name = 'land';
        """))
        rows = result.fetchall()
        if rows:
            for row in rows:
                print(f"    ✓ Table: {row[0]}, Column: {row[1]}, Type: {row[2]}, SRID: {row[3]}")
        else:
            print("    ✗ No geometry columns registered!")
            print("      The 'land' table exists but is NOT properly configured as a PostGIS table.")
        
        # Show first few rows
        print("\n[4] Sample data (first 3 rows):")
        result = conn.execute(text("SELECT * FROM land LIMIT 3;"))
        cols = result.keys()
        print(f"    Columns: {', '.join(cols)}")
        for row in result:
            print(f"    {row}")
            
    else:
        print("    ✗ Table 'land' does NOT exist")
        print("\n[2] Available tables in 'public' schema:")
        result = conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """))
        for row in result:
            print(f"    - {row[0]}")

print("\n" + "=" * 70)
