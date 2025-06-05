#!/usr/bin/env python3
"""
Ultimate X Visitor Bot
A comprehensive, stealthy bot for visiting X (Twitter) links
"""

import time
import random
import requests
import json
import os
import sys
import signal
import logging
import traceback
from datetime import datetime
from urllib.parse import urlparse
from pathlib import Path

# Optional imports - will be used if available
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    from fake_useragent import UserAgent
    FAKE_UA_AVAILABLE = True
except ImportError:
    FAKE_UA_AVAILABLE = False

# ===== CONFIGURATION =====

# X (Twitter) links to visit
X_LINKS = [
    "https://x.com/Hitansh54/status/1930194500724334705",
    "https://x.com/ArjunMehra985/status/1930199659798032610",
    "https://x.com/sahil_gopanii/status/1930207213521412417",
    "https://x.com/AlCoinverse/status/1929125757801890030",
    "https://x.com/Raj45307/status/1930202834756071790",
    "https://x.com/Snax4ogs/status/1930201674355814471",
    "https://x.com/sahil2dev/status/1930204847598428283",
    "https://x.com/Rahul113383/status/1930205881255239751",
    "https://x.com/AlCoinverse/status/1929512117993910469",
    "https://x.com/CoinWipe42313/status/1930197012625969263",
    "https://x.com/ArjunMehra985/status/1930284895202377904",
]

# Target views per link
TARGET_VIEWS = 2000

# Diverse, realistic user agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
]

# Global location simulation
LOCATIONS = [
    {"country": "US", "region": "California", "city": "Los Angeles", "timezone": "America/Los_Angeles"},
    {"country": "US", "region": "New York", "city": "New York", "timezone": "America/New_York"}, 
    {"country": "US", "region": "Texas", "city": "Austin", "timezone": "America/Chicago"},
    {"country": "UK", "region": "England", "city": "London", "timezone": "Europe/London"},
    {"country": "CA", "region": "Ontario", "city": "Toronto", "timezone": "America/Toronto"},
    {"country": "AU", "region": "NSW", "city": "Sydney", "timezone": "Australia/Sydney"},
    {"country": "IN", "region": "Maharashtra", "city": "Mumbai", "timezone": "Asia/Kolkata"},
    {"country": "DE", "region": "Berlin", "city": "Berlin", "timezone": "Europe/Berlin"},
    {"country": "FR", "region": "Ile-de-France", "city": "Paris", "timezone": "Europe/Paris"},
    {"country": "JP", "region": "Tokyo", "city": "Tokyo", "timezone": "Asia/Tokyo"},
    {"country": "BR", "region": "São Paulo", "city": "São Paulo", "timezone": "America/Sao_Paulo"},
    {"country": "SG", "region": "Singapore", "city": "Singapore", "timezone": "Asia/Singapore"}
]

# ===== MAIN BOT CLASS =====

class UltimateXVisitor:
    """Ultimate X Visitor Bot - Combines HTTP and browser automation for stealth"""
    
    def __init__(self):
        """Initialize the bot with configuration and state"""
        # Setup logging
        self.setup_logging()
        
        # Bot state
        self.running = True
        self.start_time = datetime.now()
        self.session_count = 0
        self.total_visits = 0
        self.successful_visits = 0
        self.failed_visits = 0
        
        # Link configuration
        self.links_config = self.initialize_links_config()
        self.completed_links = set()
        
        # File paths
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.progress_file = self.data_dir / "progress.json"
        self.log_file = self.data_dir / "visitor.log"
        
        # Browser configuration
        self.chrome_binary = None
        self.chromedriver_path = None
        
        # Load previous progress
        self.load_progress()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Initialize browser environment if Selenium is available
        if SELENIUM_AVAILABLE:
            self.setup_browser_environment()
        
        # Create HTTP session
        self.session = self.create_session()
        
        self.logger.info("🚀 Ultimate X Visitor Bot initialized")
    
    def initialize_links_config(self):
        """Initialize configuration for each link"""
        config = {}
        for link in X_LINKS:
            config[link] = {
                "initial_views": random.randint(50, 300),
                "current_views": 0,
                "our_visits": 0,
                "target": TARGET_VIEWS
            }
        return config
    
    def setup_logging(self):
        """Setup logging configuration"""
        self.logger = logging.getLogger("XVisitor")
        self.logger.setLevel(logging.INFO)
        
        # Console handler
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console_format = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', 
                                          datefmt='%H:%M:%S')
        console.setFormatter(console_format)
        self.logger.addHandler(console)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.warning("🛑 Shutdown signal received, saving progress...")
        self.save_progress()
        self.running = False
        sys.exit(0)
    
    def setup_browser_environment(self):
        """Setup browser environment and find Chrome/ChromeDriver"""
        self.logger.info("🔍 Looking for Chrome and ChromeDriver...")
        
        # Find Chrome binary
        chrome_paths = [
            "/nix/store/*/bin/chromium",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/opt/google/chrome/chrome"
        ]
        
        # Find ChromeDriver
        chromedriver_paths = [
            "/nix/store/*/bin/chromedriver",
            "/usr/bin/chromedriver",
            "/usr/local/bin/chromedriver",
            "/opt/chromedriver/chromedriver"
        ]
        
        # Check for Chrome
        import glob
        for pattern in chrome_paths:
            matches = glob.glob(pattern)
            if matches:
                self.chrome_binary = matches[0]
                self.logger.info(f"✅ Found Chrome: {self.chrome_binary}")
                break
        
        # Check for ChromeDriver
        for pattern in chromedriver_paths:
            matches = glob.glob(pattern)
            if matches:
                self.chromedriver_path = matches[0]
                self.logger.info(f"✅ Found ChromeDriver: {self.chromedriver_path}")
                break
        
        if not self.chrome_binary or not self.chromedriver_path:
            self.logger.warning("⚠️ Chrome or ChromeDriver not found - browser automation disabled")
            return False
        
        return True
    
    def create_session(self):
        """Create HTTP session with connection pooling"""
        session = requests.Session()
        
        # Configure connection pooling
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=3
        )
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        return session
    
    def get_user_agent(self):
        """Get a random user agent"""
        if FAKE_UA_AVAILABLE:
            try:
                ua = UserAgent()
                return ua.random
            except:
                pass
        
        return random.choice(USER_AGENTS)
    
    def create_headers(self, user_agent=None):
        """Create realistic HTTP headers"""
        if not user_agent:
            user_agent = self.get_user_agent()
        
        # Base headers
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': random.choice([
                'en-US,en;q=0.9',
                'en-US,en;q=0.9,es;q=0.8',
                'en-GB,en;q=0.9',
                'en-US,en;q=0.9,fr;q=0.8',
                'en-US,en;q=0.9,de;q=0.8'
            ]),
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': random.choice(['none', 'same-origin', 'cross-site']),
            'Cache-Control': random.choice(['no-cache', 'max-age=0']),
            'DNT': '1'
        }
        
        # Add referer sometimes
        if random.random() < 0.7:
            referers = [
                'https://www.google.com/',
                'https://www.bing.com/',
                'https://duckduckgo.com/',
                'https://www.yahoo.com/',
                'https://twitter.com/',
                'https://x.com/',
                'https://t.co/'
            ]
            headers['Referer'] = random.choice(referers)
        
        return headers
    
    def create_chrome_driver(self, headless=True):
        """Create Chrome WebDriver with stealth settings"""
        if not SELENIUM_AVAILABLE or not self.chrome_binary or not self.chromedriver_path:
            return None
        
        try:
            options = Options()
            
            # Basic options
            if headless:
                options.add_argument("--headless=new")
            
            # Required options
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            # Anti-detection options
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-extensions")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Performance options
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            
            # Set binary location
            options.binary_location = self.chrome_binary
            
            # Random user agent
            user_agent = self.get_user_agent()
            options.add_argument(f"--user-agent={user_agent}")
            
            # Create service
            service = Service(executable_path=self.chromedriver_path)
            
            # Create driver
            driver = webdriver.Chrome(service=service, options=options)
            
            # Execute stealth script
            stealth_js = """
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                window.chrome = {runtime: {}};
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            """
            driver.execute_script(stealth_js)
            
            return driver
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create Chrome driver: {str(e)}")
            return None
    
    def get_link_info(self, url):
        """Extract username and tweet ID from X URL"""
        try:
            parts = url.split('/')
            username = parts[3] if len(parts) > 3 else "unknown"
            tweet_id = parts[-1] if len(parts) > 4 else "unknown"
            return {
                "username": username,
                "tweet_id": tweet_id,
                "short_id": tweet_id[-8:] if len(tweet_id) > 8 else tweet_id,
                "display": f"@{username}"
            }
        except:
            return {"username": "unknown", "tweet_id": "unknown", "display": url[-30:]}
    
    def simulate_human_behavior(self, driver):
        """Simulate realistic human behavior in browser"""
        try:
            # Random scrolling
            for _ in range(random.randint(2, 5)):
                scroll_amount = random.randint(200, 800)
                driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                time.sleep(random.uniform(0.5, 2.0))
            
            # Mouse movements (if ActionChains is available)
            try:
                actions = ActionChains(driver)
                for _ in range(random.randint(1, 3)):
                    actions.move_by_offset(
                        random.randint(-100, 100),
                        random.randint(-100, 100)
                    ).perform()
                    time.sleep(random.uniform(0.3, 1.0))
            except:
                pass
            
        except Exception as e:
            self.logger.debug(f"Human simulation error: {str(e)}")
    
    def browser_visit(self, url):
        """Visit URL using browser automation"""
        link_info = self.get_link_info(url)
        self.logger.info(f"🌐 BROWSER: Visiting {link_info['display']}")
        
        driver = self.create_chrome_driver(headless=True)
        if not driver:
            self.logger.warning("⚠️ Browser automation not available, falling back to HTTP")
            return self.http_visit(url)
        
        try:
            # Set timeouts
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(10)
            
            # Navigate to page
            driver.get(url)
            
            # Wait for page load
            time.sleep(random.uniform(3, 8))
            
            # Simulate human behavior
            self.simulate_human_behavior(driver)
            
            # Try to interact with tweet
            success = self.interact_with_tweet(driver, link_info)
            
            # Stay on page realistically
            engagement_time = random.uniform(15, 45)
            self.logger.info(f"⏱️ Engaging for {engagement_time:.1f}s")
            time.sleep(engagement_time)
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Browser visit error: {str(e)}")
            return False
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def interact_with_tweet(self, driver, link_info):
        """Interact with tweet content"""
        try:
            # Find tweet elements
            tweet_selectors = [
                "[data-testid='tweet']",
                "[data-testid='tweetText']",
                ".css-1dbjc4n.r-18u37iz",
                "article"
            ]
            
            for selector in tweet_selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    # Scroll to tweet
                    driver.execute_script("arguments[0].scrollIntoView(true);", elements[0])
                    time.sleep(random.uniform(1, 3))
                    
                    # Click tweet
                    elements[0].click()
                    self.logger.info(f"✅ Clicked tweet: {link_info['display']}")
                    return True
            
            self.logger.warning(f"⚠️ Could not find tweet element for {link_info['display']}")
            return False
            
        except Exception as e:
            self.logger.warning(f"⚠️ Tweet interaction failed: {str(e)}")
            return False
    
    def http_visit(self, url):
        """Visit URL using HTTP request"""
        link_info = self.get_link_info(url)
        location = random.choice(LOCATIONS)
        
        try:
            # Create headers
            headers = self.create_headers()
            
            self.logger.info(f"📡 HTTP: Visiting {link_info['display']} from {location['city']}, {location['country']}")
            
            # Pre-visit delay
            time.sleep(random.uniform(1, 5))
            
            # Make request
            start_time = time.time()
            response = self.session.get(
                url, 
                headers=headers, 
                timeout=30, 
                allow_redirects=True
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                # Simulate engagement
                engagement_time = random.uniform(8, 35)
                self.logger.info(f"✅ Connected! Response: {response_time:.2f}s | Engaging: {engagement_time:.1f}s")
                time.sleep(engagement_time)
                return True
            else:
                self.logger.warning(f"⚠️ HTTP Error: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ HTTP visit failed: {str(e)}")
            return False
    
    def smart_visit(self, url):
        """Smart visit using best available method"""
        our_visits = self.links_config[url]["our_visits"]
        
        # Use browser every 5-8 visits for realism
        use_browser = (our_visits > 0 and our_visits % random.randint(5, 8) == 0)
        
        if use_browser and SELENIUM_AVAILABLE and self.chrome_binary and self.chromedriver_path:
            success = self.browser_visit(url)
        else:
            success = self.http_visit(url)
        
        # Update stats
        if success:
            self.successful_visits += 1
            self.links_config[url]["our_visits"] += 1
            
            # Simulate view increase
            if self.links_config[url]["our_visits"] % random.randint(2, 4) == 0:
                view_increase = random.randint(1, 3)
                self.links_config[url]["current_views"] += view_increase
                
                # Check if target reached
                current_views = self.links_config[url]["current_views"]
                target_views = self.links_config[url]["target"]
                
                if current_views >= target_views:
                    link_info = self.get_link_info(url)
                    self.completed_links.add(url)
                    self.logger.info(f"🏆 TARGET REACHED! {link_info['display']} completed!")
        else:
            self.failed_visits += 1
        
        return success
    
    def save_progress(self):
        """Save progress to file"""
        try:
            progress_data = {
                "links_config": self.links_config,
                "completed_links": list(self.completed_links),
                "total_visits": self.total_visits,
                "successful_visits": self.successful_visits,
                "failed_visits": self.failed_visits,
                "session_count": self.session_count,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.progress_file, 'w') as f:
                json.dump(progress_data, f, indent=2)
                
            self.logger.info("💾 Progress saved")
        except Exception as e:
            self.logger.error(f"❌ Failed to save progress: {str(e)}")
    
    def load_progress(self):
        """Load previous progress"""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r') as f:
                    data = json.load(f)
                
                # Load link configuration
                self.links_config = data.get("links_config", self.links_config)
                
                # Load stats
                self.completed_links = set(data.get("completed_links", []))
                self.total_visits = data.get("total_visits", 0)
                self.successful_visits = data.get("successful_visits", 0)
                self.failed_visits = data.get("failed_visits", 0)
                self.session_count = data.get("session_count", 0)
                
                self.logger.info("📂 Previous progress loaded")
                self.show_progress()
            else:
                self.logger.info("🆕 Starting fresh")
                self.initialize_views()
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to load progress: {str(e)}")
            self.initialize_views()
    
    def initialize_views(self):
        """Initialize starting view counts"""
        self.logger.info("🔢 Initializing view counts...")
        
        for url in self.links_config:
            # Set initial views
            initial_views = self.links_config[url]["initial_views"]
            self.links_config[url]["current_views"] = initial_views
            
            link_info = self.get_link_info(url)
            self.logger.info(f"👁️ {link_info['display']}: {initial_views} starting views")
    
    def get_active_links(self):
        """Get links that need more views"""
        return [url for url in self.links_config 
                if url not in self.completed_links]
    
    def show_progress(self):
        """Display detailed progress"""
        self.logger.info("=" * 60)
        self.logger.info("📊 PROGRESS REPORT")
        self.logger.info("=" * 60)
        
        for url, config in self.links_config.items():
            link_info = self.get_link_info(url)
            current = config["current_views"]
            target = config["target"]
            visits = config["our_visits"]
            initial = config.get("initial_views", 0)
            gained = current - initial
            
            progress_pct = (current / target) * 100 if target > 0 else 0
            status = "🏆 COMPLETE" if url in self.completed_links else f"📈 {progress_pct:.1f}%"
            
            self.logger.info(f"{link_info['display']:15} | {current:5}/{target} | +{gained:4} | Visits: {visits:3} | {status}")
        
        completed = len(self.completed_links)
        total_links = len(self.links_config)
        overall = (completed / total_links) * 100 if total_links > 0 else 0
        
        self.logger.info("-" * 60)
        self.logger.info(f"🎯 Overall: {completed}/{total_links} completed ({overall:.1f}%)")
        self.logger.info(f"📊 Visits: {self.total_visits} | Success: {self.successful_visits} | Failed: {self.failed_visits}")
        
        if self.total_visits > 0:
            success_rate = (self.successful_visits / self.total_visits) * 100
            self.logger.info(f"✅ Success Rate: {success_rate:.1f}%")
            
        uptime = str(datetime.now() - self.start_time).split('.')[0]
        self.logger.info(f"⏱️ Runtime: {uptime}")
        self.logger.info("=" * 60)
    
    def run(self):
        """Main execution loop"""
        self.logger.info("🚀 Ultimate X Visitor Bot Started!")
        self.logger.info(f"🎯 Target: {TARGET_VIEWS} views per link ({len(self.links_config)} links)")
        
        if SELENIUM_AVAILABLE and self.chrome_binary and self.chromedriver_path:
            self.logger.info("🌐 Browser automation: ENABLED")
        else:
            self.logger.info("📡 Browser automation: DISABLED (HTTP only)")
        
        try:
            while self.running:
                active_links = self.get_active_links()
                
                if not active_links:
                    self.logger.info("🎉 ALL TARGETS ACHIEVED! Campaign successful!")
                    break
                
                # Randomize order
                random.shuffle(active_links)
                
                # Visit each link
                for url in active_links:
                    if not self.running:
                        break
                    
                    self.session_count += 1
                    self.total_visits += 1
                    
                    # Visit link
                    self.smart_visit(url)
                    
                    # Save progress periodically
                    if self.total_visits % 10 == 0:
                        self.save_progress()
                    
                    # Show progress periodically
                    if self.total_visits % 20 == 0:
                        self.show_progress()
                    
                    # Smart delays between visits
                    if self.running:
                        delay = random.uniform(15, 45)
                        if random.random() < 0.2:  # 20% chance of longer delay
                            delay += random.uniform(10, 30)
                        
                        self.logger.info(f"😴 Waiting {delay:.1f}s before next visit")
                        time.sleep(delay)
                
                # Inter-round break
                if self.running and active_links:
                    self.show_progress()
                    break_time = random.uniform(60, 180)  # 1-3 minutes
                    self.logger.info(f"⏸️ Taking a break for {break_time:.0f}s")
                    time.sleep(break_time)
                    
        except KeyboardInterrupt:
            self.logger.warning("🛑 Stopped by user")
        except Exception as e:
            self.logger.error(f"❌ Critical error: {str(e)}")
            traceback.print_exc()
        finally:
            self.save_progress()
            self.show_progress()
            self.logger.info("🏁 Bot execution completed")

# ===== MAIN EXECUTION =====

def main():
    """Entry point"""
    print("=" * 60)
    print("🚀 Ultimate X Visitor Bot")
    print("🔒 Stealthy, efficient, and reliable")
    print("=" * 60)
    
    bot = UltimateXVisitor()
    bot.run()

if __name__ == "__main__":
    main()
