"""
Diagnostic script to identify PostgreSQL connection issues.
This helps determine if Python is connecting to the same instance as psql.
"""

import os
import sys
import socket
import subprocess
from urllib.parse import quote_plus

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

# Try to get psql configuration via environment variables
print("\nEnvironment variables that might affect psql:")
for var in ["PGHOST", "PGPORT", "PGUSER", "PGPASSWORD", "PGDATABASE"]:
    value = os.environ.get(var)
    if value:
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
    result = sock.connect_ex(('localhost', 2528))
    sock.close()
    if result == 0:
        print("✓ Port 2528 is OPEN and accepting connections")
    else:
        print(f"✗ Port 2528 is CLOSED or not responding (error code: {result})")
        print("  → Check if PostgreSQL is running on port 2528")
except Exception as e:
    print(f"✗ Connection error: {e}")

# ============================================================================
# STEP 3: Check with psycopg2 (what Python will use)
# ============================================================================
print("\n[STEP 3] Testing direct psycopg2 connection (without password)...")
try:
    import psycopg2
    from psycopg2 import OperationalError
    
    # Test connection WITHOUT password (might work if peer auth enabled)
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=2528,
            user="postgres",
            database="agrie_state"
        )
        print("✓ Connected without password (peer authentication enabled)")
        
        # Get server version
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"  Server version: {version}")
        
        cursor.close()
        conn.close()
    except OperationalError as e:
        error_msg = str(e)
        print(f"✗ Connection without password failed:")
        print(f"  {error_msg}")
        
        # Check if error contains useful info
        if "password authentication" in error_msg.lower():
            print("  → Password authentication is REQUIRED")
        if "connection refused" in error_msg.lower():
            print("  → PostgreSQL not running on port 2528")
        if "database" in error_msg.lower() and "does not exist" in error_msg.lower():
            print("  → Database 'agrie_state' not found")
            
except ImportError:
    print("✗ psycopg2 not installed")

# ============================================================================
# STEP 4: Show what connection string Python will use
# ============================================================================
print("\n[STEP 4] PostgreSQL connection string (without actual password)...")
password_placeholder = "***"
engine_string = f"postgresql+psycopg2://postgres:{password_placeholder}@localhost:2528/agrie_state"
print(f"  {engine_string}")

# Test with actual password
print("\n[STEP 5] Testing SQLAlchemy connection with your actual password...")
try:
    password = os.getenv("POSTGRES_PASSWORD")  # Your password
    
    # Show what quote_plus does to the password
    encoded_password = quote_plus(password)
    print(f"  Raw password length: {len(password)} chars")
    print(f"  After quote_plus: length {len(encoded_password)} chars")
    if password != encoded_password:
        print(f"  ⚠ Password was encoded (special chars detected)")
    
    engine = create_engine(
        f"postgresql+psycopg2://postgres:{encoded_password}@localhost:2528/agrie_state",
        echo=False
    )
    
    # Try to connect
    with engine.connect() as connection:
        print("✓ SQLAlchemy connection SUCCESSFUL!")
        result = connection.execute("SELECT version();")
        version = result.fetchone()[0]
        print(f"  Server version: {version}")
        
except Exception as e:
    error_msg = str(e)
    print(f"✗ SQLAlchemy connection FAILED:")
    print(f"  {error_msg}")
    
    # Provide specific guidance
    if "password authentication failed" in error_msg.lower():
        print("\n  DIAGNOSIS: Password authentication is failing.")
        print("  This could mean:")
        print("    1. Different PostgreSQL instance (different port config)")
        print("    2. Password mismatch between psql and Python")
        print("    3. Character encoding issue in password")
        print("    4. Connection pooling or host resolution issue")

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
