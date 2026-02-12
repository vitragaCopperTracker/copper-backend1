#!/usr/bin/env python3
"""
WebDriver utilities for Selenium automation
"""

import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def init_driver():
    """Initialize Chrome WebDriver with optimized options for speed"""
    try:
        chrome_options = Options()
        
        # Speed optimization options
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-javascript")  # Faster loading
        chrome_options.add_argument("--disable-css")  # Even faster
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--window-size=1024,768")  # Smaller window
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        # Performance settings
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        # Check if running in Docker or server environment
        # Check multiple indicators: dockerenv file, server_config env var, or Railway env
        is_docker = (
            os.path.exists('/.dockerenv') or 
            os.environ.get('server_config') in ['True', 'true', '1'] or
            os.environ.get('RAILWAY_ENVIRONMENT') is not None or
            os.path.exists('/usr/bin/chromium')  # Chromium installed = likely Docker
        )
        
        if is_docker:
            logging.info("Running in Docker/server environment")
            chrome_options.binary_location = "/usr/bin/chromium"
            service = Service("/usr/bin/chromedriver")
        else:
            logging.info("Running in local environment")
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
            except Exception as e:
                logging.warning(f"WebDriver manager failed: {e}")
                service = Service()
        
        # Initialize driver with faster timeouts
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(15)  # Reduced timeout
        driver.implicitly_wait(3)  # Reduced wait time
        
        logging.info("WebDriver initialized successfully")
        return driver
        
    except Exception as e:
        logging.error(f"Failed to initialize WebDriver: {e}")
        return None