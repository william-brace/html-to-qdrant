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

def download_with_selenium(driver, link, output_path, state_code, filename):
    """Attempt to download page using Selenium"""
    driver.get(link)
    time.sleep(2)  # Wait for page to load
    html_content = driver.page_source
    
    content = remove_elements(html_content, state_code)
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(f"<!--SOURCE_URL:{link}-->\n")
        file.write(content)
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
    parser.add_argument('--collection-name', required=True,
                       help='Collection name format with {state} placeholder')
    return parser.parse_args()

def get_directory_name(collection_name: str, state_code: str) -> str:
    """Generate directory name based on collection name format"""
    return f"websites-{collection_name.format(state=state_code.lower())}"

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
    """Download state-specific links using wget"""
    print(f"\nProcessing {state_code} using wget...")
    
    for idx, link in enumerate(links):
        filename = f'pfl{str(idx)}.html'
        output_path = os.path.join(directory, filename)
        
        # Check if file already exists and skip if it does
        if os.path.exists(output_path):
            print(f"⏭️ File already exists: {filename}")
            continue
            
        wget_command = f'wget --no-check-certificate --content-disposition -P {directory} -O {os.path.join(directory, filename)} "{link}"'
        
        if not run_wget_command(wget_command, link, state_code):
            print(f"Failed to download {link}")
            continue
        
        print(f"✅ Successfully downloaded: {filename}")
        
        # Add a small delay between downloads
        time.sleep(1)

def main():
    args = parse_args()
    
    # Define states that should use wget
    wget_states = {'nj', 'or'}  # Add any states that need wget
    
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
            
            # Create state-specific directory
            if state_lower in state_map:
                directory = get_directory_name(args.collection_name, state_map[state_lower][1])
                if not os.path.exists(directory):
                    os.makedirs(directory)
                
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
                        driver = setup_driver()
                    
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