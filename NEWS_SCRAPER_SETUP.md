# Copper News Scraper Setup

## Overview
The news scraper (Process 6) collects copper-related news from 6 major mining news websites and stores them in the `api_app_generalnews` database table.

## Database Table

### Table: `api_app_generalnews`

Created by running: `python3 create_copper_news_table.py`

**Schema:**
```sql
CREATE TABLE api_app_generalnews (
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
```

**Indexes:**
- `idx_generalnews_source` - For filtering by news source
- `idx_generalnews_created_at` - For sorting by creation date
- `idx_generalnews_date` - For filtering by article date
- `api_app_generalnews_url_key` - Unique constraint on URL (prevents duplicates)

## News Sources

### 1. Mining.com
- **URL:** https://www.mining.com/?s=copper
- **Articles per run:** 4
- **Content:** Full article content (paragraphs + headings)
- **Data extracted:** Title, content, image, date

### 2. Mining Review
- **URL:** https://www.miningreview.com/?s=copper
- **Articles per run:** 4
- **Content:** Full article content (paragraphs, headings, lists)
- **Data extracted:** Title, content, summary, featured image, date
- **Special:** Extracts background images from CSS

### 3. LPPM.com
- **URL:** https://www.lppm.com/news
- **Articles per run:** 4
- **Content:** Full article content
- **Data extracted:** Title, content, summary, date
- **Special:** Human-like scrolling to avoid detection

### 4. MiningMX
- **URL:** https://www.miningmx.com/news/copper/
- **Articles per run:** All available
- **Content:** Metadata only (no full content)
- **Data extracted:** Title, image, date

### 5. Metals Daily
- **URL:** https://www.metalsdaily.com/news/copper-news/
- **Articles per run:** All available
- **Content:** Title + heading only
- **Data extracted:** Title, content (heading), date
- **Special:** Fastest scraper (no article visits)

### 6. Mining Weekly
- **URL:** https://www.miningweekly.com/page/copper
- **Articles per run:** All available
- **Content:** Summary
- **Data extracted:** Title, summary, image, date
- **Special:** Fallback date extraction from URL

## How It Works

### Process Flow
1. **Process 6 starts** when `current_process = "process6"` in database
2. **Scrapes each source** sequentially with error handling
3. **Checks for duplicates** using URL before inserting
4. **Inserts into database** using `insert_general_news()` function
5. **Updates process** to "process1" when complete
6. **Cycle continues** indefinitely

### Duplicate Prevention
- Each scraper checks if URL exists before processing: `check_url_exists(cursor, url)`
- Database has UNIQUE constraint on `url` column
- `ON CONFLICT DO UPDATE` ensures no duplicate entries

### Error Handling
- Each source wrapped in try-except block
- If one source fails, others continue
- Errors logged but don't stop the process

## Running the Scrapers

### Create the table (one-time setup):
```bash
cd copper_python1
python3 create_copper_news_table.py
```

### Run all processes (including news scraper):
```bash
python3 app.py
```

### Run only news scraper (for testing):
```python
from database_config import get_curser
from database_operations import update_process_status

connection, cursor = get_curser()
update_process_status(cursor, connection, "process6")
cursor.close()
connection.close()

# Then run app.py
python3 app.py
```

## Database Operations

### Insert News Article
```python
from database_operations import insert_general_news

insert_general_news(
    cursor, connection,
    source="Mining.com",
    title="Article Title",
    url="https://example.com/article",
    content="Full article content...",
    summary="Article summary",
    image_url="https://example.com/image.jpg",
    date="2026-02-12"
)
```

### Check if URL Exists
```python
from insert_queries import check_url_exists

exists = check_url_exists(cursor, "https://example.com/article")
```

### Get Recent News
```python
from database_operations import get_recent_general_news

# Get 50 most recent articles
news = get_recent_general_news(cursor, limit=50)

# Get recent articles from specific source
news = get_recent_general_news(cursor, limit=50, source="Mining.com")
```

### Get Statistics
```python
from database_operations import get_general_news_stats

stats = get_general_news_stats(cursor)
# Returns: total_articles, unique_sources, oldest_article, newest_article, articles_with_images
```

### Delete Old News
```python
from database_operations import delete_old_general_news

# Delete articles older than 90 days
deleted_count = delete_old_general_news(cursor, connection, days_old=90)
```

## Files

- `create_copper_news_table.py` - Table creation script
- `news_scrape.py` - All 6 news scrapers
- `database_operations.py` - Database functions for news
- `insert_queries.py` - URL existence checking
- `app.py` - Main application (Process 6 implementation)
- `webdriver_utils.py` - Selenium WebDriver setup

## Deployment

The news scraper runs automatically in the Docker container on Railway:
- Dockerfile includes Chromium and ChromeDriver
- Xvfb provides virtual display for headless browsing
- Environment variable `server_config=True` enables Docker mode
- Process cycles continuously through all 6 processes

## Monitoring

Check logs for:
- Articles scraped per source
- Total articles in each run
- Errors from specific scrapers
- Database insertion success/failure

Example log output:
```
2026-02-12 18:00:00 - INFO - Process 6: General News Scraper
2026-02-12 18:00:05 - INFO - Mining.com: 4 articles
2026-02-12 18:00:10 - INFO - Mining Review: 4 articles
2026-02-12 18:00:15 - INFO - LPPM.com: 4 articles
2026-02-12 18:00:20 - INFO - MiningMX: 8 articles
2026-02-12 18:00:25 - INFO - Metals Daily: 12 articles
2026-02-12 18:00:30 - INFO - Mining Weekly: 10 articles
2026-02-12 18:00:30 - INFO - Process 6 completed - Total articles: 42
```

## Troubleshooting

### Table doesn't exist
```bash
python3 create_copper_news_table.py
```

### Scraper fails
- Check Selenium/ChromeDriver installation
- Verify website structure hasn't changed
- Check network connectivity
- Review error logs

### Duplicate entries
- Should not happen due to UNIQUE constraint
- Check `check_url_exists()` is being called
- Verify URL normalization

### No articles scraped
- Websites may have changed HTML structure
- Update CSS selectors in `news_scrape.py`
- Check if websites are accessible

## Future Improvements

1. Add retry logic for failed scrapers
2. Implement rate limiting between requests
3. Add content validation before insertion
4. Create separate scraper execution (don't fail all if one fails)
5. Add monitoring/alerting for scraper failures
6. Implement incremental scraping (only new articles)
7. Add article categorization/tagging
8. Implement full-text search on content
