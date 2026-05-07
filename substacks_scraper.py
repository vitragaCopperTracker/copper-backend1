def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-setuid-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(5)
    return driver


def scrape_substack_copper_posts(cursor=None, max_posts=10):
    driver = init_driver()
    if not driver:
        logging.error("Failed to initialize WebDriver")
        return []
    
    try:
        print("Navigating to Substack search page...")
        search_url = "https://substack.com/search/copper?sort=new&searching=all_posts"
        driver.get(search_url)
        
        # longer wait for JS to load
        print("Waiting for search results...")
        time.sleep(8)

        # scroll slowly like a human
        print("Loading more content...")
        for _ in range(5):
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(1.5)

        # print page source for debugging
        print(f"Page title: {driver.title}")
        print(f"Page URL: {driver.current_url}")

        # try multiple selectors
        print("Finding article links...")
        links = []
        
        selectors = [
            "a[href*='/p/']",
            "a.post-preview-title",
            "h2 a",
            "h3 a",
            "div.post-preview a",
        ]
        
        for selector in selectors:
            links = driver.find_elements(By.CSS_SELECTOR, selector)
            if links:
                print(f"Found {len(links)} links with selector: {selector}")
                break
        
        print(f"Found {len(links)} links")

        urls = []
        seen_urls = set()
        for link in links:
            try:
                url = link.get_attribute('href')
                if url and url not in seen_urls and '/p/' in url and 'substack.com' in url:
                    urls.append(url)
                    seen_urls.add(url)
                    if len(urls) >= max_posts:
                        break
            except:
                continue

        print(f"Found {len(urls)} unique URLs to scrape")

        scraped_data = []
        for url in urls:
            try:
                print(f"Scraping URL: {url}")
                driver.get(url)
                time.sleep(3)
                
                article = wait_and_find_element(driver, By.TAG_NAME, "article", timeout=10)
                if not article:
                    print("Article content not found, skipping...")
                    continue

                title = None
                for selector in ["h1.post-title", "h1[class*='title']", "h1"]:
                    try:
                        elem = driver.find_element(By.CSS_SELECTOR, selector)
                        if elem and elem.text.strip():
                            title = elem.text.strip()
                            break
                    except:
                        continue

                content = None
                for selector in ["div.available-content", "div.body", "article"]:
                    try:
                        elem = driver.find_element(By.CSS_SELECTOR, selector)
                        if elem and elem.text.strip():
                            content = elem.text.strip()
                            break
                    except:
                        continue

                date = datetime.now().strftime("%Y-%m-%d")
                try:
                    date_elem = driver.find_element(By.TAG_NAME, "time")
                    date_str = date_elem.get_attribute("datetime")
                    if date_str:
                        date = date_str.split("T")[0]
                except:
                    pass

                image_url = ""
                try:
                    img = driver.find_element(By.CSS_SELECTOR, "img.post-image, article img")
                    image_url = img.get_attribute("src") or ""
                except:
                    pass

                if title and content:
                    scraped_data.append({
                        "title": title,
                        "url": url,
                        "content": content,
                        "subtitle": "",
                        "image_url": image_url,
                        "date": date
                    })
                    print(f"Successfully scraped: {title[:50]}...")

            except Exception as e:
                print(f"Error scraping {url}: {e}")
                continue

        print(f"Successfully scraped {len(scraped_data)} Substack posts")
        return scraped_data
        
    except Exception as e:
        print(f"Error in scraping Substack: {e}")
        return []
    finally:
        if driver:
            driver.quit()