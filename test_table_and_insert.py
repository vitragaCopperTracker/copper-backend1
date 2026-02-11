#!/usr/bin/env python3
"""
Test script to check if table exists, create it if needed, and test insertion
"""

import sys
import time
from database_config import get_curser
from database_operations import insert_general_news, check_general_news_url_exists, get_general_news_stats

def create_table_if_not_exists():
    """Create the general news table if it doesn't exist"""
    try:
        connection, cursor = get_curser()
        print("✅ Database connection established")
        
        # Create table SQL
        create_table_query = """
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
        """
        
        print("📝 Creating table if not exists...")
        cursor.execute(create_table_query)
        connection.commit()
        print("✅ Table ready!")
        
        # Create indexes
        print("📝 Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_generalnews_url ON api_app_generalnews(url);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_generalnews_date ON api_app_generalnews(date);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_generalnews_source ON api_app_generalnews(source);")
        connection.commit()
        print("✅ Indexes ready!")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        return False

def test_insertion():
    """Test inserting a sample article"""
    try:
        connection, cursor = get_curser()
        
        # Test article
        test_article = {
            'source': 'Test Source',
            'title': 'Test Copper News Article',
            'url': f'https://test.com/article-{int(time.time())}',
            'content': 'This is a test article about copper mining.',
            'summary': 'Test summary',
            'image_url': 'https://test.com/image.jpg',
            'date': '2024-02-11'
        }
        
        print("\n📰 Testing article insertion...")
        print(f"   Title: {test_article['title']}")
        print(f"   URL: {test_article['url']}")
        
        # Insert the article
        success = insert_general_news(
            cursor, connection,
            source=test_article['source'],
            title=test_article['title'],
            url=test_article['url'],
            content=test_article['content'],
            summary=test_article['summary'],
            image_url=test_article['image_url'],
            date=test_article['date']
        )
        
        if success:
            print("✅ Article inserted successfully!")
            
            # Verify it exists
            exists = check_general_news_url_exists(cursor, test_article['url'])
            print(f"✅ Article verified in database: {exists}")
            
            # Get stats
            stats = get_general_news_stats(cursor)
            if stats:
                print("\n📊 Database Statistics:")
                print(f"   Total articles: {stats['total_articles']}")
                print(f"   Unique sources: {stats['unique_sources']}")
                print(f"   Articles with images: {stats['articles_with_images']}")
        else:
            print("❌ Article insertion failed")
        
        cursor.close()
        connection.close()
        return success
        
    except Exception as e:
        print(f"❌ Error testing insertion: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 80)
    print("GENERAL NEWS TABLE TEST")
    print("=" * 80)
    
    # Step 1: Create table if needed
    print("\n[STEP 1] Creating table if not exists...")
    if not create_table_if_not_exists():
        print("❌ Failed to create table")
        sys.exit(1)
    
    # Step 2: Test insertion
    print("\n[STEP 2] Testing article insertion...")
    if not test_insertion():
        print("❌ Failed to insert test article")
        sys.exit(1)
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED!")
    print("=" * 80)
    print("\nThe general news table is ready for use.")
    print("You can now run process6 to scrape and insert real articles.\n")

if __name__ == "__main__":
    main()
