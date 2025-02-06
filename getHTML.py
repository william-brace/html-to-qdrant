# import wget 
from links import linksCO, linksNY, linksMA, linksCA, linksWA, linksRI, linksDC, linksCT, gen 
# import wget
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import subprocess
import argparse

# for file_number, link in enumerate(linksRI):
    
#     filename = f'pfl{str(file_number)}.html'
#     output_path = os.path.join("websites", filename)
#     wget.download(link, out=output_path)


# Create array of arrays with state codes
state_links = [
    # (linksCO, "CO"), # All good
    # (linksNY, "NY"), # All good
    (linksMA, "MA"), # Errors
    # (linksCA, "CA"), # All
    (linksWA, "WA"), # Errors
    # (linksRI, "RI"), # All Good
    (linksDC, "DC"), # Errors
    # (linksCT, "CT") # All Good
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0'
}

def create_session():
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.headers.update(headers)
    return session

def download_with_requests(link, output_path, state_code, filename):
    """Attempt to download page using requests library"""
    response = requests.get(link, headers=headers)
    response.raise_for_status()
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(response.text)
    print(f"Downloaded (requests): {state_code}/{filename}")

def download_with_selenium(driver, link, output_path, state_code, filename):
    """Attempt to download page using Selenium"""
    driver.get(link)
    time.sleep(2)  # Wait for page to load
    html_content = driver.page_source
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(html_content)
    print(f"Downloaded (selenium): {state_code}/{filename}")

def setup_driver():
    """Initialize and configure Selenium WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--states', nargs='+', help='List of state codes to process')
    return parser.parse_args()

def run_wget_command(command: str) -> bool:
    """Execute wget command and return success status"""
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"✅ Successfully executed wget command: {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error executing wget command: {str(e)}")
        return False

def main():
    args = parse_args()
    
    # Special handling for NJ and OR using wget commands
    wget_commands = {
        'nj': 'wget -r -np -nd -A.html,.txt,.tmp -P websites-nj https://www.nj.gov/labor/myleavebenefits/',
        'or': 'wget -r -np -nd -A.txt,.tmp -P websites-or https://paidleave.oregon.gov/'
    }
    
    # If states are provided via command line, use those instead of default
    if args.states:
        state_links = []
        state_map = {
            'co': (linksCO, "CO"),
            'ny': (linksNY, "NY"),
            'ma': (linksMA, "MA"),
            'ca': (linksCA, "CA"),
            'wa': (linksWA, "WA"),
            'ri': (linksRI, "RI"),
            'dc': (linksDC, "DC"),
            'ct': (linksCT, "CT"),
            'general': (gen, "general")
        }
        
        for state in args.states:
            state_lower = state.lower()
            # Handle wget commands for NJ and OR
            if state_lower in wget_commands:
                if not run_wget_command(wget_commands[state_lower]):
                    print(f"Failed to process {state.upper()} using wget")
                continue
            
            # Handle other states using existing method
            if state_lower in state_map:
                state_links.append(state_map[state_lower])
    
    driver = None
    try:
        for links, state_code in state_links:
            # Create state-specific directory if it doesn't exist
            directory = f'websites-{state_code.lower()}'
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            print(f"\nProcessing {state_code}...")
            
            # Download files for current state
            for file_number, link in enumerate(links):
                filename = f'pfl{str(file_number)}.html'
                output_path = os.path.join(directory, filename)
                
                # Try simple requests approach first
                try:
                    download_with_requests(link, output_path, state_code, filename)
                    
                except (requests.exceptions.RequestException, Exception) as err:
                    print(f"******* REQUESTS method failed for {state_code}/{filename}: {err}")
                    print("Trying Selenium...")
                    
                    # Initialize driver only if needed
                    if driver is None:
                        driver = setup_driver()
                    
                    try:
                        download_with_selenium(driver, link, output_path, state_code, filename)
                    except Exception as selenium_err:
                        print(f"******* SELENIUM method failed failed for {state_code}/{filename}: {selenium_err}")

    finally:
        if driver:
            driver.quit()

    print("\nAll downloads completed.")

if __name__ == "__main__":
    main() 