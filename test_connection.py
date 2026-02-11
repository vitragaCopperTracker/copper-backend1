#!/usr/bin/env python3
import psycopg2
from database_config import get_curser

try:
    print("Testing database connection...")
    connection, cursor = get_curser()
    print("✅ Connected successfully!")
    
    # Test a simple query
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"PostgreSQL version: {version[0]}")
    
    cursor.close()
    connection.close()
    print("✅ Connection test passed!")
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    import traceback
    traceback.print_exc()
