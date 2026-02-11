# copper_python1

Copper data collection pipeline - scrapes and stores copper-related news, stock data, press releases, substacks, and YouTube videos.

## Features
- Process 1: Stock data fetcher (224 copper stocks)
- Process 2: Press release scraper
- Process 3: Stock news scraper
- Process 4: Substack article scraper
- Process 5: YouTube video scraper
- Process 6: General copper news scraper (Mining.com, Mining Review, MiningMX, Metals Daily, Mining Weekly)

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Configure `.env` with database credentials
3. Run `python set_process.py` to select process
4. Run `python app.py` to start scraping

## Database
Uses PostgreSQL on Railway.app to store all scraped data.
