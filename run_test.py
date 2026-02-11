#!/usr/bin/env python3
"""Quick test of news scraper"""
from news_scrape import scrape_latest_articles_from_mining_site

print("\n" + "="*80)
print("COPPER NEWS SCRAPER TEST - Mining.com")
print("="*80 + "\n")

print("Scraping: https://www.mining.com/?s=copper\n")

articles = scrape_latest_articles_from_mining_site(None)

print(f"\n✅ Found {len(articles)} articles\n")

if articles:
    print("Sample articles:\n")
    for i, a in enumerate(articles[:5], 1):
        print(f"[{i}] {a.get('title', 'No title')[:70]}...")
        print(f"    Date: {a.get('date', 'N/A')}")
        print(f"    URL: {a.get('url', 'N/A')[:70]}...")
        if a.get('content'):
            print(f"    Content: {a['content'][:100]}...")
        print()
else:
    print("⚠️  No articles found - website may have changed structure\n")

print("="*80 + "\n")
