"""
Diagnostic script to identify PostgreSQL connection issues.
This helps determine if Python is connecting to the same instance as psql.
"""

import os
import sys
import socket
import subprocess
from urllib.parse import quote_plus

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

print("=" * 70)
print("POSTGRESQL CONNECTION DIAGNOSTIC")
print("=" * 70)


# ============================================================================
# STEP 1: Check which PostgreSQL instance psql uses
# ============================================================================
print("\n[STEP 1] Finding psql configuration...")

try:
    result = subprocess.run(
        ["psql", "--version"],
        capture_output=True,
        text=True,
        timeout=5
    )

    print(f"✓ psql version: {result.stdout.strip()}")

except Exception as e:
    print(f"✗ Error running psql --version: {e}")


# Check environment variables
print("\nEnvironment variables that might affect psql:")

for var in ["PGHOST", "PGPORT", "PGUSER", "PGPASSWORD", "PGDATABASE"]:

    value = os.environ.get(var)

    if value:
        # Don't display password
        if var == "PGPASSWORD":
            print(f"  {var}=********")
        else:
            print(f"  {var}={value}")

    else:
        print(f"  {var}=(not set)")


# ============================================================================
# STEP 2: Check if localhost:2528 is accessible
# ============================================================================
print("\n[STEP 2] Testing connectivity to localhost:2528...")

try:

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)

    result = sock.connect_ex(("localhost", 2528))

    sock.close()

    if result == 0:

        print("✓ Port 2528 is OPEN and accepting connections")

    else:

        print(
            f"✗ Port 2528 is CLOSED or not responding "
            f"(error code: {result})"
        )

        print("  → Check if PostgreSQL is running on port 2528")

except Exception as e:

    print(f"✗ Connection error: {e}")


# ============================================================================
# STEP 3: Check with psycopg2 without password
# ============================================================================
print("\n[STEP 3] Testing direct psycopg2 connection (without password)...")

try:

    import psycopg2
    from psycopg2 import OperationalError

    try:

        conn = psycopg2.connect(
            host="localhost",
            port=2528,
            user="postgres",
            database="agrie_state"
        )

        print("✓ Connected without password")

        cursor = conn.cursor()

        cursor.execute("SELECT version();")

        version = cursor.fetchone()[0]

        print(f"  Server version: {version}")

        cursor.close()
        conn.close()

    except OperationalError as e:

        error_msg = str(e)

        print("✗ Connection without password failed:")
        print(f"  {error_msg}")

        if "password authentication" in error_msg.lower():

            print("  → Password authentication is REQUIRED")

        if "connection refused" in error_msg.lower():

            print("  → PostgreSQL not running on port 2528")

        if (
            "database" in error_msg.lower()
            and "does not exist" in error_msg.lower()
        ):

            print("  → Database 'agrie_state' not found")

except ImportError:

    print("✗ psycopg2 not installed")


# ============================================================================
# STEP 4: Show connection string without actual password
# ============================================================================
print("\n[STEP 4] PostgreSQL connection string (without actual password)...")

password_placeholder = "***"

engine_string = (
    f"postgresql+psycopg2://postgres:"
    f"{password_placeholder}@localhost:2528/agrie_state"
)

print(f"  {engine_string}")


# ============================================================================
# STEP 5: Test SQLAlchemy connection using .env password
# ============================================================================
print("\n[STEP 5] Testing SQLAlchemy connection using .env password...")

try:

    # Read password from .env
    password = os.getenv("POSTGRES_PASSWORD")

    if not password:

        raise ValueError(
            "POSTGRES_PASSWORD not found in .env file"
        )

    # Encode special characters safely
    encoded_password = quote_plus(password)

    print(f"  Password found in .env: YES")
    print(f"  Password length: {len(password)} characters")
    print(f"  Encoded password length: {len(encoded_password)} characters")

    if password != encoded_password:

        print("  ⚠ Password was encoded (special characters detected)")

    # Create SQLAlchemy engine
    engine = create_engine(
        f"postgresql+psycopg2://postgres:"
        f"{encoded_password}@localhost:2528/agrie_state",
        echo=False
    )

    print("✓ SQLAlchemy engine created")

    # Test connection
    with engine.connect() as connection:

        print("✓ SQLAlchemy connection SUCCESSFUL!")

        result = connection.execute(
            text("SELECT version();")
        )

        version = result.fetchone()[0]

        print(f"  Server version: {version}")

        # Check current database
        result = connection.execute(
            text("SELECT current_database();")
        )

        database = result.fetchone()[0]

        print(f"  Current database: {database}")

        # Check current user
        result = connection.execute(
            text("SELECT current_user;")
        )

        user = result.fetchone()[0]

        print(f"  Current user: {user}")


except Exception as e:

    error_msg = str(e)

    print("✗ SQLAlchemy connection FAILED:")
    print(f"  {error_msg}")

    if "password authentication failed" in error_msg.lower():

        print("\n  DIAGNOSIS: Password authentication is failing.")

        print("  Possible reasons:")

        print("    1. Password in .env is incorrect")
        print("    2. Different PostgreSQL instance")
        print("    3. PostgreSQL is using a different port")
        print("    4. PostgreSQL password was changed")
        print("    5. Connection settings are incorrect")


# ============================================================================
# STEP 6: List running PostgreSQL processes
# ============================================================================
print("\n[STEP 6] PostgreSQL processes running...")

try:

    result = subprocess.run(
        ["tasklist", "/FI", "IMAGENAME eq postgres.exe"],
        capture_output=True,
        text=True,
        timeout=5
    )

    if "postgres.exe" in result.stdout:

        print("✓ PostgreSQL processes found:")
        print(result.stdout)

    else:

        print("✗ No PostgreSQL processes found")

except Exception as e:

    print(f"✗ Error checking processes: {e}")


print("\n" + "=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)