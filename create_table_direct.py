#!/usr/bin/env python3
"""
Direct table creation using DATABASE_PUBLIC_URL
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Use the public URL directly
DATABASE_URL = os.getenv('DATABASE_PUBLIC_URL')

print("=" * 80)
print("Creating General News Table (Direct Connection)")
print("=" * 80)

try:
    print(f"\nConnecting to database...")
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()
    print("✅ Connected successfully!")
    
    # Create table
    print("\n📝 Creating table api_app_generalnews...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_app_generalnews (
            id VARCHAR(255) PRIMARY KEY,
            source VARCHAR(255) NOT NULL,
            title TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            content TEXT,
            summary TEXT,
            image_url TEXT,
            date DATE,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)
    connection.commit()
    print("✅ Table created!")
    
    # Create indexes
    print("\n📝 Creating indexes...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_generalnews_url ON api_app_generalnews(url);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_generalnews_date ON api_app_generalnews(date);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_generalnews_source ON api_app_generalnews(source);")
    connection.commit()
    print("✅ Indexes created!")
    
    # Verify
    print("\n🔍 Verifying table...")
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'api_app_generalnews'
        ORDER BY ordinal_position;
    """)
    columns = cursor.fetchall()
    print("\n📋 Table structure:")
    for col in columns:
        print(f"   - {col[0]:20s} : {col[1]}")
    
    cursor.close()
    connection.close()
    
    print("\n" + "=" * 80)
    print("✅ SUCCESS! Table created and ready to use!")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
