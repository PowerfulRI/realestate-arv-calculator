"""
Browser setup utility for Selenium-based web scraping.
"""
import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import WebDriverException

from ..config.settings import HEADLESS_BROWSER, BROWSER_USER_AGENT, SCRAPE_TIMEOUT

logger = logging.getLogger(__name__)

def setup_chrome_browser(headless=None):
    """
    Set up a Chrome browser for web scraping with advanced anti-detection measures.
    
    Args:
        headless: Override the default headless setting from config
        
    Returns:
        WebDriver: Configured Chrome WebDriver instance
    """
    if headless is None:
        headless = HEADLESS_BROWSER
        
    # Import random here to avoid circular imports
    import random
    
    # Configure Chrome options
    chrome_options = Options()
    
    # Realistic user agent - updated regularly to match current Chrome versions
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    ]
    chosen_user_agent = random.choice(user_agents)
    chrome_options.add_argument(f"--user-agent={chosen_user_agent}")
    
    # Create a dedicated user data directory to maintain cookies and sessions
    import tempfile
    import os
    user_data_dir = os.path.join(tempfile.gettempdir(), f"chrome_user_data_{random.randint(1000, 9999)}")
    os.makedirs(user_data_dir, exist_ok=True)
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    
    # Headless mode setup - non-headless is better for real estate sites
    if headless:
        # Modern headless still has some detection vectors, so disable only in production
        chrome_options.add_argument("--headless=new")
    
    # Common settings for better scraping
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Add randomization to window size to appear more human-like
    width = random.randint(1200, 1920)
    height = random.randint(800, 1080)
    chrome_options.add_argument(f"--window-size={width},{height}")
    
    # Set a default download directory
    download_dir = os.path.join(tempfile.gettempdir(), f"chrome_downloads_{random.randint(1000, 9999)}")
    os.makedirs(download_dir, exist_ok=True)
    
    # Add language preferences with randomization
    languages = [
        "en-US,en;q=0.9",
        "en-US,en;q=0.9,es;q=0.8",
        "en-GB,en;q=0.9",
        "en-CA,en;q=0.9,fr-CA;q=0.8",
    ]
    chrome_options.add_argument(f"--lang={random.choice(languages)}")
    
    # Add additional settings to avoid detection
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    # Add advanced preferences to mimic real browser
    prefs = {
        "profile.default_content_setting_values.notifications": 2,  # Block notifications
        "credentials_enable_service": False,  # Disable password manager
        "profile.password_manager_enabled": False,
        "profile.default_content_settings.popups": 0,
        "profile.managed_default_content_settings.images": 1,  # Load images
        "profile.default_content_setting_values.cookies": 1,  # Allow cookies
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        # Randomize geolocation permissions to appear more human
        "profile.default_content_setting_values.geolocation": random.choice([0, 1, 2]),
        # Set a custom default zoom level for more randomness
        "default_zoom_level": random.choice([0, 1, -1])
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Try to use a proxy if available (commented out by default)
    # proxies = [
    #    "123.456.789.012:8080",
    #    "234.567.890.123:8080"
    # ]
    # if random.choice([True, False]):  # 50% chance to use a proxy
    #    proxy = random.choice(proxies)
    #    chrome_options.add_argument(f'--proxy-server={proxy}')
    
    try:
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        # Set reasonable timeouts
        driver.set_page_load_timeout(SCRAPE_TIMEOUT)
        driver.set_script_timeout(SCRAPE_TIMEOUT)
        
        # Execute CDP commands to prevent detection
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                // Overwrite the 'webdriver' property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Overwrite the plugins array with fake plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => {
                        // Create a more realistic plugins array
                        const pluginArray = new PluginArray();
                        const pluginCount = Math.floor(Math.random() * 10) + 1;
                        
                        for (let i = 0; i < pluginCount; i++) {
                            const fakePlugin = {
                                name: ['PDF Viewer', 'Chrome PDF Viewer', 'Native Client', 
                                       'Chrome PDF Plugin', 'Widevine Content Decryption Module'][Math.floor(Math.random() * 5)],
                                description: 'Portable Document Format',
                                filename: 'internal-pdf-viewer',
                                length: 1
                            };
                            Object.defineProperty(pluginArray, i, {
                                value: fakePlugin,
                                enumerable: true
                            });
                        }
                        
                        Object.defineProperty(pluginArray, 'length', {
                            value: pluginCount,
                            enumerable: false
                        });
                        
                        return pluginArray;
                    }
                });
                
                // Overwrite the languages property
                Object.defineProperty(navigator, 'languages', {
                    get: () => {
                        const languages = ['en-US', 'en', 'es', 'fr', 'de'];
                        const count = Math.floor(Math.random() * 3) + 1;
                        return languages.slice(0, count);
                    }
                });
                
                // Add hardware concurrency randomization
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    get: () => Math.floor(Math.random() * 8) + 2
                });
                
                // Add device memory randomization
                Object.defineProperty(navigator, 'deviceMemory', {
                    get: () => Math.floor(Math.random() * 8) + 2
                });
                
                // Prevent detection via webdriver fingerprinting
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' || 
                    parameters.name === 'geolocation' ||
                    parameters.name === 'midi' ||
                    parameters.name === 'microphone' ||
                    parameters.name === 'camera' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
                
                // Fake notification API
                if (Notification.permission !== 'denied') {
                    Notification.permission = ['default', 'granted'][Math.floor(Math.random() * 2)];
                }
                
                // Override connection property
                const connectionProperties = {
                    effectiveType: ['4g', '3g', '2g', 'slow-2g'][Math.floor(Math.random() * 4)],
                    rtt: Math.floor(Math.random() * 100) + 50,
                    downlink: Math.floor(Math.random() * 10) + 1,
                    saveData: Math.random() > 0.5
                };
                
                if (navigator.connection) {
                    Object.defineProperties(navigator.connection, {
                        effectiveType: { get: () => connectionProperties.effectiveType },
                        rtt: { get: () => connectionProperties.rtt },
                        downlink: { get: () => connectionProperties.downlink },
                        saveData: { get: () => connectionProperties.saveData }
                    });
                }
            """
        })
        
        # Add random mouse movements and scrolls to simulate human behavior
        import time
        
        # Initial delay to let the page load
        time.sleep(random.uniform(2, 5))
        
        # Simulate human-like interactions
        def add_human_interaction(driver):
            try:
                # Random scrolling
                scroll_amount = random.randint(50, 500)
                driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                time.sleep(random.uniform(0.5, 1.5))
                
                # More scrolling with variation
                if random.random() > 0.5:
                    scroll_amount = random.randint(100, 300)
                    driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                    time.sleep(random.uniform(0.3, 0.7))
                    
                    # Sometimes scroll back up a bit
                    if random.random() > 0.7:
                        scroll_amount = -random.randint(50, 150)
                        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                        time.sleep(random.uniform(0.3, 0.7))
            except:
                # Ignore errors in the human interaction simulation
                pass
        
        # Add initial human-like behavior
        add_human_interaction(driver)
        
        # Add a method to the driver for human-like interaction
        driver.add_human_interaction = add_human_interaction
        
        return driver
    except WebDriverException as e:
        logger.error(f"Failed to initialize Chrome browser: {str(e)}")
        raise

def setup_firefox_browser(headless=None):
    """
    Set up a Firefox browser for web scraping as a fallback option.
    
    Args:
        headless: Override the default headless setting from config
        
    Returns:
        WebDriver: Configured Firefox WebDriver instance
    """
    if headless is None:
        headless = HEADLESS_BROWSER
        
    # Configure Firefox options
    firefox_options = FirefoxOptions()
    if headless:
        firefox_options.add_argument("--headless")
    
    # Set user agent
    firefox_options.set_preference("general.useragent.override", BROWSER_USER_AGENT)
    
    # Disable WebDriver mode
    firefox_options.set_preference("dom.webdriver.enabled", False)
    firefox_options.set_preference('useAutomationExtension', False)
    
    try:
        driver = webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()),
            options=firefox_options
        )
        
        # Set page load timeout
        driver.set_page_load_timeout(SCRAPE_TIMEOUT)
        
        return driver
    except WebDriverException as e:
        logger.error(f"Failed to initialize Firefox browser: {str(e)}")
        raise

def get_browser(browser_type="chrome", headless=None):
    """
    Get a configured browser for web scraping.
    
    Args:
        browser_type: Type of browser to use ("chrome" or "firefox")
        headless: Override the default headless setting from config
        
    Returns:
        WebDriver: Configured WebDriver instance
    """
    try:
        if browser_type.lower() == "chrome":
            return setup_chrome_browser(headless)
        elif browser_type.lower() == "firefox":
            return setup_firefox_browser(headless)
        else:
            logger.warning(f"Unsupported browser type: {browser_type}. Using Chrome.")
            return setup_chrome_browser(headless)
    except Exception as e:
        logger.error(f"Failed to initialize browser: {str(e)}")
        if browser_type.lower() == "chrome":
            logger.info("Trying Firefox as fallback...")
            return setup_firefox_browser(headless)
        else:
            logger.info("Trying Chrome as fallback...")
            return setup_chrome_browser(headless)

def safely_navigate(driver, url, max_retries=3, wait_time=2):
    """
    Safely navigate to a URL with retry mechanism.
    
    Args:
        driver: WebDriver instance
        url: URL to navigate to
        max_retries: Maximum number of retry attempts
        wait_time: Time to wait between retries in seconds
        
    Returns:
        bool: True if navigation was successful, False otherwise
    """
    for attempt in range(max_retries):
        try:
            driver.get(url)
            return True
        except Exception as e:
            logger.warning(f"Navigation attempt {attempt+1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(wait_time)
            else:
                logger.error(f"Failed to navigate to {url} after {max_retries} attempts")
                return False