# import wget 
from links import linksCA, linksCO, linksNY, linksMA, linksWA, linksRI, linksDC, linksCT, gen, linksNJ, linksOR
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
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import certifi
import ssl
import urllib3

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create unverified context and set as default
ssl._create_default_https_context = ssl._create_unverified_context

# for file_number, link in enumerate(linksRI):
    
#     filename = f'pfl{str(file_number)}.html'
#     output_path = os.path.join("websites", filename)
#     wget.download(link, out=output_path)


# Create array of arrays with state codes - used onlyt when getHTML.py is run directly, otherwise orchestrator passes the state_links through arg
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

# Define elements to remove for each state
ELEMENTS_TO_REMOVE = {
    'nj': [
        '.footer',
        '.sonj-nav'
    ],
    # Add configurations for other states as needed
}

def create_session():
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.headers.update(headers)
    return session

def remove_elements(html_content, state_code):
    """Remove specified elements from HTML content using BeautifulSoup"""
    if state_code not in ELEMENTS_TO_REMOVE:
        print(f"No elements to remove for state {state_code}")
        return html_content
        
    soup = BeautifulSoup(html_content, 'html.parser')
    print(f"Processing removals for state {state_code}")
    
    for selector in ELEMENTS_TO_REMOVE[state_code]:
        print(f"Attempting to remove elements matching: {selector}")
        # Handle different types of selectors
        if selector.startswith('.'):  # Class selector
            class_name = selector[1:]  # Remove the leading dot
            elements = soup.find_all(class_=class_name)
        elif selector.startswith('#'):  # ID selector
            elements = soup.find_all(id=selector[1:])
        else:  # Tag name or custom selector
            elements = soup.select(selector)
            
        print(f"Found {len(elements)} matching elements")
        for element in elements:
            print(f"Removing element: {element.name} with classes: {element.get('class', [])}")
            element.decompose()
    
    return str(soup)

def download_with_requests(link, output_path, state_code, filename):
    """Attempt to download page using requests library"""
    response = requests.get(link, headers=headers)
    response.raise_for_status()
    content = remove_elements(response.text, state_code)
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(f"<!--SOURCE_URL:{link}-->\n")
        file.write(content)
    print(f"Downloaded (requests): {state_code}/{filename}")

def setup_fast_driver():
    """Initialize quick headless driver for simple sites"""
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return uc.Chrome(options=options)

def setup_stealth_driver():
    """Initialize anti-detection driver for protected sites"""
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--ignore-certificate-errors-spki-list')
    return uc.Chrome(options=options)

def quick_selenium_download(driver, link, output_path, state_code, filename):
    """Fast download attempt for simple sites"""
    try:
        driver.get(link)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        
        html_content = driver.page_source
        
        # Check for common blocking indicators
        if any(x in html_content.lower() for x in [
            "just a moment", "verify you are human", "captcha", 
            "403 forbidden", "access denied"
        ]):
            raise Exception("Bot detection encountered")
            
        content = remove_elements(html_content, state_code)
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(f"<!--SOURCE_URL:{link}-->\n")
            file.write(content)
        print(f"✓ Quick download successful: {state_code}/{filename}")
        return True
    except Exception as e:
        print(f"Quick download failed: {str(e)}")
        return False

def stealth_selenium_download(driver, link, output_path, state_code, filename):
    """Enhanced download with anti-detection measures"""
    try:
        # time.sleep(random.uniform(5, 10))
        driver.get(link)
        
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        
        # Check for Cloudflare "Just a moment..." page
        max_retries = 5
        current_retry = 0
        
        while current_retry < max_retries:
            html_content = driver.page_source
            
            if "Just a moment..." in html_content:
                print(f"⏳ Waiting for Cloudflare check on {filename}...")
                time.sleep(random.uniform(5, 7))
                driver.refresh()
                current_retry += 1
                continue
            break
            
        if current_retry == max_retries:
            raise Exception(f"Failed to bypass Cloudflare after {max_retries} attempts")
        
        html_content = driver.page_source
        content = remove_elements(html_content, state_code)
        
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(f"<!--SOURCE_URL:{link}-->\n")
            file.write(content)
        print(f"✓ Stealth download successful: {state_code}/{filename}")
        return True
    except Exception as e:
        print(f"Stealth download failed: {str(e)}")
        return False

def download_with_selenium(driver, link, output_path, state_code, filename):
    """Two-tiered download approach"""
    # Try fast download first
    fast_driver = None
    stealth_driver = None
    
    try:
        print(f"Attempting quick download for {filename}...")
        fast_driver = setup_fast_driver()
        if quick_selenium_download(fast_driver, link, output_path, state_code, filename):
            return
        
        # If fast download fails, try stealth mode
        print(f"Quick download failed. Switching to stealth mode for {filename}...")
        stealth_driver = setup_stealth_driver()
        if not stealth_selenium_download(stealth_driver, link, output_path, state_code, filename):
            raise Exception("Both download methods failed")
            
    except Exception as e:
        print(f"Error in download process: {str(e)}")
        raise
    finally:
        # Clean up drivers
        if fast_driver:
            fast_driver.quit()
        if stealth_driver:
            stealth_driver.quit()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--states', nargs='+', help='List of state codes to process')
    parser.add_argument('--collection-name', required=True,
                       help='Collection name format with {state} placeholder')
    return parser.parse_args()

def get_directory_name(collection_name: str, state_code: str) -> str:
    """Generate directory name based on collection name format"""
    return f"websites-{collection_name.format(state=state_code.lower())}"

def ensure_fresh_directory(directory: str):
    """Delete directory if it exists, then create a fresh one"""
    if os.path.exists(directory):
        print(f"Removing existing directory: {directory}")
        import shutil
        shutil.rmtree(directory)
    print(f"Creating fresh directory: {directory}")
    os.makedirs(directory)

def run_wget_command(command: str, original_url: str, state_code: str) -> bool:
    """Execute wget command and return success status"""
    try:
        print(f"Executing wget command: {command}")  # Debug logging
        
        # Run wget command
        subprocess.run(command, shell=True, check=True)
        
        # Get output directory and filename from the command
        output_path = command.split(' -O ')[1].split(' ')[0]
        print(f"Output path: {output_path}")  # Debug logging
        
        # Process only the specific output file
        if os.path.exists(output_path):
            try:
                with open(output_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Apply element removal
                content = remove_elements(content, state_code.lower())
                
                # Write content with original URL
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f"<!--SOURCE_URL:{original_url}-->\n")
                    f.write(content)
                
                print(f"Successfully processed file: {output_path}")  # Debug logging
                return True
                
            except Exception as e:
                print(f"Error processing file {output_path}: {str(e)}")
                return False
        else:
            print(f"Output file not found: {output_path}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error executing wget command: {str(e)}")
        return False

def download_state_with_wget(links: list, state_code: str, directory: str):
    """Download state-specific links using wget with fallback to requests/selenium"""
    print(f"\nProcessing {state_code} using wget...")
    
    driver = None  # Initialize driver only if needed
    
    for idx, link in enumerate(links):
        filename = f'pfl{str(idx)}.html'
        output_path = os.path.join(directory, filename)
        
        # Check if file already exists and skip if it does
        if os.path.exists(output_path):
            print(f"⏭️ File already exists: {filename}")
            continue
            
        wget_command = f'wget --no-check-certificate --content-disposition -P {directory} -O {os.path.join(directory, filename)} "{link}"'
        
        # Try wget first
        if not run_wget_command(wget_command, link, state_code):
            print(f"Wget failed for {link}, trying requests...")
            
            # Try requests as first fallback
            try:
                download_with_requests(link, output_path, state_code, filename)
                print(f"✅ Successfully downloaded with requests: {filename}")
                continue
            except Exception as req_err:
                print(f"Requests failed for {state_code}/{filename}: {req_err}")
                print("Trying Selenium as final fallback...")
                
                # Try Selenium as final fallback
                try:
                    if driver is None:
                        driver = setup_stealth_driver()
                    download_with_selenium(driver, link, output_path, state_code, filename)
                    print(f"✅ Successfully downloaded with Selenium: {filename}")
                except Exception as selenium_err:
                    print(f"❌ All download methods failed for {state_code}/{filename}")
                    print(f"Final error: {selenium_err}")
        else:
            print(f"✅ Successfully downloaded with wget: {filename}")
        
        # Add a small delay between downloads
        time.sleep(1)
    
    # Clean up Selenium driver if it was used
    if driver:
        driver.quit()

def main():
    args = parse_args()
    
    # Define states that should use wget
    wget_states = {'nj', 'or', 'ri'}  # Add any states that need wget
    
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
            'nj': (linksNJ, "NJ"),
            'or': (linksOR, "OR"),
            'general': (gen, "general")
        }
        
        for state in args.states:
            state_lower = state.lower()
            
            # Create fresh state-specific directory
            if state_lower in state_map:
                directory = get_directory_name(args.collection_name, state_map[state_lower][1])
                ensure_fresh_directory(directory)
                
                # Use wget for specified states
                if state_lower in wget_states:
                    download_state_with_wget(
                        state_map[state_lower][0],
                        state_map[state_lower][1],
                        directory
                    )
                else:
                    # Use existing method for other states
                    state_links.append(state_map[state_lower])

    # Process remaining states with original method
    driver = None
    try:
        for links, state_code in state_links:
            # Create state-specific directory if it doesn't exist
            directory = get_directory_name(args.collection_name, state_code)
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            print(f"\nProcessing {state_code}...")
            
            # Original download logic for non-wget states
            for file_number, link in enumerate(links):
                filename = f'pfl{str(file_number)}.html'
                output_path = os.path.join(directory, filename)
                
                try:
                    download_with_requests(link, output_path, state_code, filename)
                except (requests.exceptions.RequestException, Exception) as err:
                    print(f"******* REQUESTS method failed for {state_code}/{filename}: {err}")
                    print("Trying Selenium...")
                    
                    if driver is None:
                        driver = setup_stealth_driver()
                    
                    try:
                        download_with_selenium(driver, link, output_path, state_code, filename)
                    except Exception as selenium_err:
                        print(f"******* SELENIUM method failed for {state_code}/{filename}: {selenium_err}")

    finally:
        if driver:
            driver.quit()

    print("\nAll downloads completed.")

if __name__ == "__main__":
    main() 