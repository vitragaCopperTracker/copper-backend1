"""
YouTube Videos Updater Script for Copper Content
"""

import sys
import os
from datetime import datetime, timedelta
from youtube_search import YoutubeSearch
import logging
import re
import requests

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database_config import get_curser
from database_operations import (
    check_youtube_video_url_exists,
    insert_youtube_video,
    delete_all_youtube_videos
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_youtube_publish_time(publish_time_str):
    try:
        if not publish_time_str:
            return datetime.now().date()
        
        publish_time_str = publish_time_str.lower().strip()
        
        if 'hour' in publish_time_str or 'h ago' in publish_time_str:
            hours = int(re.search(r'(\d+)', publish_time_str).group(1))
            return (datetime.now() - timedelta(hours=hours)).date()
        elif 'day' in publish_time_str or 'd ago' in publish_time_str:
            days = int(re.search(r'(\d+)', publish_time_str).group(1))
            return (datetime.now() - timedelta(days=days)).date()
        elif 'week' in publish_time_str or 'w ago' in publish_time_str:
            weeks = int(re.search(r'(\d+)', publish_time_str).group(1))
            return (datetime.now() - timedelta(weeks=weeks)).date()
        elif 'month' in publish_time_str or 'mo ago' in publish_time_str:
            months = int(re.search(r'(\d+)', publish_time_str).group(1))
            return (datetime.now() - timedelta(days=months * 30)).date()
        elif 'year' in publish_time_str or 'y ago' in publish_time_str:
            years = int(re.search(r'(\d+)', publish_time_str).group(1))
            return (datetime.now() - timedelta(days=years * 365)).date()
        else:
            logger.warning(f"Could not parse publish time: {publish_time_str}")
            return datetime.now().date()
            
    except Exception as e:
        logger.error(f"Error parsing publish time '{publish_time_str}': {e}")
        return datetime.now().date()

def clean_views(raw_views):
    try:
        return int(str(raw_views).replace(',', '').replace('views', '').strip())
    except:
        return 0

def search_youtube_videos(query, max_results=10):
    try:
        logger.info(f"Searching YouTube for: {query}")
        
        search_results = YoutubeSearch(query, max_results=max_results * 5).to_dict()
        
        video_list = []

        for video in search_results:
            thumbnails = video.get('thumbnails', [])
            if not thumbnails or len(thumbnails) == 0:
                logger.info(f"Skipping video without thumbnail: {video.get('title', 'Unknown')}")
                continue
            
            url_suffix = video.get('url_suffix', '')
            if '/watch?v=' not in url_suffix:
                logger.info(f"Skipping video with invalid URL: {video.get('title', 'Unknown')}")
                continue
            
            video_id = url_suffix.split('/watch?v=')[1].split('&')[0] if '/watch?v=' in url_suffix else None
            if not video_id or len(video_id) != 11:
                logger.info(f"Skipping video with invalid video ID: {video.get('title', 'Unknown')}")
                continue
            
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
            
            duration = video.get('duration', '')
            if duration and ':' in duration:
                try:
                    parts = duration.split(':')
                    if len(parts) == 2:
                        minutes, seconds = int(parts[0]), int(parts[1])
                        total_seconds = minutes * 60 + seconds
                        if total_seconds < 30:
                            logger.info(f"Skipping very short video ({duration}): {video.get('title', 'Unknown')}")
                            continue
                except:
                    pass

            video_list.append({
                'title': video.get('title', ''),
                'link': f"https://www.youtube.com{url_suffix}",
                'duration': duration,
                'views': clean_views(video.get('views', '')),
                'channel': video.get('channel', ''),
                'publish_time': video.get('publish_time', ''),
                'parsed_date': parse_youtube_publish_time(video.get('publish_time', '')),
                'video_id': video_id,
                'thumbnail_url': thumbnail_url
            })
        
        video_list.sort(key=lambda x: x['parsed_date'], reverse=True)
        final_videos = video_list[:max_results]
        
        logger.info(f"Found {len(final_videos)} valid videos for query: {query}")
        return final_videos
        
    except Exception as e:
        logger.error(f"Error searching YouTube for '{query}': {e}")
        return []

def is_relevant_video(title, channel, duration):
    text = (title + ' ' + channel).lower()
    
    required_keywords = [
        'copper', 'copper mining', 'copper price', 'copper market', 'copper stocks',
        'copper futures', 'copper investment', 'industrial metals', 'base metals',
        'mining', 'commodity', 'metal prices', 'copper demand', 'copper supply'
    ]
    
    exclude_keywords = [
        'music', 'song', 'album', 'concert', 'gaming', 'game', 'movie', 'film',
        'recipe', 'cooking', 'fashion', 'beauty', 'sports', 'football', 'basketball',
        'unboxing', 'reaction', 'prank', 'challenge', 'tiktok', 'shorts compilation',
        'copper wire diy', 'copper pipe', 'copper plumbing', 'copper jewelry making'
    ]
    
    exclude_channels = [
        'music', 'entertainment', 'gaming', 'kids', 'cartoon', 'anime',
        'reaction', 'compilation', 'funny', 'meme', 'diy', 'crafts'
    ]
    
    has_required = any(keyword in text for keyword in required_keywords)
    has_excluded = any(keyword in text for keyword in exclude_keywords)
    has_excluded_channel = any(keyword in channel.lower() for keyword in exclude_channels)
    
    if duration:
        try:
            parts = duration.split(':')
            if len(parts) == 2:
                minutes = int(parts[0])
                if minutes > 120:
                    return False
                if minutes < 1:
                    return False
        except:
            pass
    
    return has_required and not has_excluded and not has_excluded_channel

def extract_company_info(title, channel):
    companies = {
        'freeport': {'name': 'Freeport-McMoRan', 'ticker': 'FCX'},
        'freeport mcmoran': {'name': 'Freeport-McMoRan', 'ticker': 'FCX'},
        'southern copper': {'name': 'Southern Copper Corporation', 'ticker': 'SCCO'},
        'grupo mexico': {'name': 'Grupo Mexico', 'ticker': 'GMEXICOB'},
        'bhp': {'name': 'BHP Group', 'ticker': 'BHP'},
        'rio tinto': {'name': 'Rio Tinto', 'ticker': 'RIO'},
        'glencore': {'name': 'Glencore', 'ticker': 'GLEN'},
        'antofagasta': {'name': 'Antofagasta', 'ticker': 'ANTO'},
        'codelco': {'name': 'Codelco', 'ticker': 'CODELCO'},
        'teck resources': {'name': 'Teck Resources', 'ticker': 'TECK'},
        'first quantum': {'name': 'First Quantum Minerals', 'ticker': 'FM'},
        'lundin mining': {'name': 'Lundin Mining', 'ticker': 'LUN'},
        'hudbay minerals': {'name': 'Hudbay Minerals', 'ticker': 'HBM'},
        'taseko mines': {'name': 'Taseko Mines', 'ticker': 'TKO'},
        'copper mountain': {'name': 'Copper Mountain Mining', 'ticker': 'CMMC'},
        'ero copper': {'name': 'Ero Copper', 'ticker': 'ERO'},
        'ivanhoe mines': {'name': 'Ivanhoe Mines', 'ticker': 'IVN'},
        'capstone copper': {'name': 'Capstone Copper', 'ticker': 'CS'},
        'amerigo resources': {'name': 'Amerigo Resources', 'ticker': 'ARG'},
        'trilogy metals': {'name': 'Trilogy Metals', 'ticker': 'TMQ'}
    }
    
    text = (title + ' ' + channel).lower()
    
    for key, info in companies.items():
        if key in text:
            return info['name'], info['ticker']
    
    return None, None

def scrape_youtube_videos():
    logger.info("=" * 60)
    logger.info("Starting YouTube Videos Scraping for Copper Content")
    logger.info("=" * 60)
    
    search_queries = {
        'Featured': [
            'copper market analysis',
            'copper price forecast',
            'copper investment outlook',
            'copper vs gold investment',
            'copper demand supply'
        ],
        'Company': [
            'copper mining stocks',
            'Freeport McMoRan news',
            'Southern Copper earnings',
            'BHP copper production',
            'Rio Tinto copper mining',
            'copper mining companies'
        ],
        'Podcast': [
            'copper market podcast',
            'mining podcast',
            'commodity trading podcast',
            'copper investment interview',
            'industrial metals podcast'
        ],
        'Education': [
            'what is copper metal',
            'how copper is mined',
            'copper uses applications',
            'copper market explained',
            'copper investment guide',
            'industrial metals explained'
        ]
    }
    
    all_videos = {}
    
    try:
        for category, queries in search_queries.items():
            logger.info(f"\nProcessing category: {category}")
            all_videos_for_category = []
            
            for query in queries:
                logger.info(f"  Searching with query: '{query}'")
                videos = search_youtube_videos(query, max_results=5)
                all_videos_for_category.extend(videos)
            
            if all_videos_for_category:
                unique_videos = []
                seen_urls = set()
                for video in all_videos_for_category:
                    if video['link'] not in seen_urls:
                        unique_videos.append(video)
                        seen_urls.add(video['link'])
                
                final_videos = unique_videos[:8]
                all_videos[category] = final_videos
                logger.info(f"  Total unique videos for {category}: {len(final_videos)}")
            else:
                logger.warning(f"No videos found for category '{category}'")
                all_videos[category] = []
        
        total_videos = sum(len(videos) for videos in all_videos.values())
        logger.info("=" * 60)
        logger.info(f"YouTube Videos Scraping Complete! Total: {total_videos}")
        logger.info("=" * 60)
        
        return all_videos
        
    except Exception as e:
        logger.error(f"Fatal error during YouTube videos scraping: {e}")
        raise

def main():
    try:
        connection, cursor = get_curser()
        logger.info("Connected to database successfully")
        
        # scrape first
        all_videos = scrape_youtube_videos()
        
        total_new = sum(len(videos) for videos in all_videos.values())
        
        # only cleanup if we actually found new videos
        if total_new > 0:
            logger.info(f"Found {total_new} new videos, cleaning up old ones...")
            cursor.execute("""
                DELETE FROM api_app_videopagedata 
                WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '3 months'
            """)
            connection.commit()
            logger.info("Old videos cleaned up")
        else:
            logger.warning("No new videos found — skipping cleanup to preserve existing DB data")
        
        total_inserted = 0
        for category, videos in all_videos.items():
            if videos:
                logger.info(f"\nInserting videos for category: {category}")
                inserted_count = 0
                
                for video in videos:
                    try:
                        if check_youtube_video_url_exists(cursor, video['link']):
                            logger.info(f"Video already exists, skipping: {video['title'][:50]}...")
                            continue
                        
                        company_name, stock_ticker = extract_company_info(
                            video['title'],
                            video['channel']
                        )
                        
                        success = insert_youtube_video(
                            cursor=cursor,
                            connection=connection,
                            video_category=category,
                            video_link=video['link'],
                            channel_name=video['channel'],
                            date=video['parsed_date'],
                            title=video['title'],
                            company_name=company_name,
                            stock_ticker=stock_ticker,
                            thumbnail_url=video.get('thumbnail_url'),
                            duration=video.get('duration'),
                            views=video.get('views'),
                            video_id=video.get('video_id')
                        )
                        
                        if success:
                            inserted_count += 1
                        
                    except Exception as e:
                        logger.warning(f"Failed to insert video '{video['title'][:50]}...': {e}")
                        continue
                
                logger.info(f"Inserted {inserted_count} videos for category '{category}'")
                total_inserted += inserted_count
        
        logger.info(f"Total videos inserted: {total_inserted}")

    except Exception as e:
        logger.error(f"Script failed: {e}")
        raise
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
        logger.info("Database connection closed")

if __name__ == "__main__":
    main()