# bot/integrations/chrome_webdriver.py
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def init_driver():
    # Base directory 
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Detect the OS
    if os.name == 'nt':
        driver_path = os.path.join(base_dir, "chromedriver-win64", "chromedriver.exe")
    else:  # Assuming Linux
        driver_path = os.path.join(base_dir, "chromedriver-linux64", "chromedriver")

    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('start-maximized')
    chrome_options.add_argument('disable-infobars')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--log-level=3') 

    # Initialize the WebDriver
    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    return driver
