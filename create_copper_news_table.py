#!/usr/bin/env python3
"""
Create Copper News Table Script

This script creates the api_app_generalnews table in the database
for storing general copper news from various mining news websites.
"""

import logging
from database_config import get_curser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_copper_news_table():
    """Create the api_app_generalnews table if it doesn't exist"""
    
    try:
        # Get database connection
        connection, cursor = get_curser()
        logger.info("Connected to database successfully")
        
        # Create table SQL
        create_table_query = """
        CREATE TABLE IF NOT EXISTS api_app_generalnews (
            id VARCHAR(255) PRIMARY KEY,
            source VARCHAR(100) NOT NULL,
            title TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            content TEXT,
            summary TEXT,
            image_url TEXT,
            date DATE,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        logger.info("Creating api_app_generalnews table...")
        cursor.execute(create_table_query)
        
        # Create indexes for better query performance
        logger.info("Creating indexes...")
        
        # Index on source for filtering by news source
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_generalnews_source 
            ON api_app_generalnews(source);
        """)
        
        # Index on created_at for sorting by date
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_generalnews_created_at 
            ON api_app_generalnews(created_at DESC);
        """)
        
        # Index on date for filtering by article date
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_generalnews_date 
            ON api_app_generalnews(date DESC);
        """)
        
        # Commit the changes
        connection.commit()
        logger.info("✅ Table api_app_generalnews created successfully!")
        logger.info("✅ Indexes created successfully!")
        
        # Display table structure
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'api_app_generalnews'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        logger.info("\n" + "=" * 80)
        logger.info("TABLE STRUCTURE: api_app_generalnews")
        logger.info("=" * 80)
        for col in columns:
            col_name, data_type, max_length, nullable = col
            length_info = f"({max_length})" if max_length else ""
            null_info = "NULL" if nullable == "YES" else "NOT NULL"
            logger.info(f"  {col_name:20} {data_type}{length_info:15} {null_info}")
        logger.info("=" * 80)
        
        # Display indexes
        cursor.execute("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = 'api_app_generalnews';
        """)
        
        indexes = cursor.fetchall()
        logger.info("\nINDEXES:")
        logger.info("=" * 80)
        for idx in indexes:
            logger.info(f"  {idx[0]}")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Error creating table: {e}")
        if 'connection' in locals():
            connection.rollback()
        raise
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
        logger.info("Database connection closed")

def verify_table_exists():
    """Verify that the table was created successfully"""
    try:
        connection, cursor = get_curser()
        
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'api_app_generalnews'
            );
        """)
        
        exists = cursor.fetchone()[0]
        
        if exists:
            # Get row count
            cursor.execute("SELECT COUNT(*) FROM api_app_generalnews;")
            count = cursor.fetchone()[0]
            
            logger.info(f"\n✅ Table verification successful!")
            logger.info(f"   Table: api_app_generalnews")
            logger.info(f"   Current rows: {count}")
            return True
        else:
            logger.error("❌ Table does not exist!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error verifying table: {e}")
        return False
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("COPPER NEWS TABLE CREATION SCRIPT")
    logger.info("=" * 80)
    
    try:
        # Create the table
        create_copper_news_table()
        
        # Verify it was created
        verify_table_exists()
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ SCRIPT COMPLETED SUCCESSFULLY!")
        logger.info("=" * 80)
        logger.info("\nThe api_app_generalnews table is ready to store news from:")
        logger.info("  - Mining.com")
        logger.info("  - Mining Review")
        logger.info("  - LPPM.com")
        logger.info("  - MiningMX")
        logger.info("  - Metals Daily")
        logger.info("  - Mining Weekly")
        logger.info("\nYou can now run the news scrapers to populate the table.")
        
    except Exception as e:
        logger.error(f"\n❌ Script failed: {e}")
        exit(1)
