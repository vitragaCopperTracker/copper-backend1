"""
Simple insert queries for press releases and news articles
"""

def check_press_release_url_exists(cursor, url):
    """Check if a press release URL already exists in the database"""
    try:
        check_query = "SELECT COUNT(*) FROM api_app_pressreleases WHERE url = %s;"
        cursor.execute(check_query, (url,))
        count = cursor.fetchone()[0]
        return count > 0
    except Exception as e:
        print(f"Error checking press release URL existence: {e}")
        return False

def check_stock_news_url_exists(cursor, url):
    """Check if a stock news URL already exists in the database"""
    try:
        check_query = "SELECT COUNT(*) FROM api_app_stocknews WHERE url = %s;"
        cursor.execute(check_query, (url,))
        count = cursor.fetchone()[0]
        return count > 0
    except Exception as e:
        print(f"Error checking stock news URL existence: {e}")
        return False

def check_url_exists(cursor, url):
    """
    Generic function to check if a URL exists in any news table.
    Used by news_scrape.py for general news articles.
    
    Checks multiple tables:
    - api_app_pressreleases
    - api_app_stocknews
    - api_app_generalnews (if exists)
    """
    if not cursor or not url:
        return False
    
    try:
        # Check in press releases
        cursor.execute("SELECT COUNT(*) FROM api_app_pressreleases WHERE url = %s;", (url,))
        if cursor.fetchone()[0] > 0:
            return True
        
        # Check in stock news
        cursor.execute("SELECT COUNT(*) FROM api_app_stocknews WHERE url = %s;", (url,))
        if cursor.fetchone()[0] > 0:
            return True
        
        # Check in general news table if it exists
        try:
            cursor.execute("SELECT COUNT(*) FROM api_app_generalnews WHERE url = %s;", (url,))
            if cursor.fetchone()[0] > 0:
                return True
        except:
            pass  # Table might not exist
        
        return False
        
    except Exception as e:
        print(f"Error checking URL existence: {e}")
        return False