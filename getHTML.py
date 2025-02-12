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
        # Write both the content and the source URL
        file.write(f"<!--SOURCE_URL:{link}-->\n")
        file.write(response.text)
    print(f"Downloaded (requests): {state_code}/{filename}")

def download_with_selenium(driver, link, output_path, state_code, filename):
    """Attempt to download page using Selenium"""
    driver.get(link)
    time.sleep(2)  # Wait for page to load
    html_content = driver.page_source
    with open(output_path, 'w', encoding='utf-8') as file:
        # Write both the content and the source URL
        file.write(f"<!--SOURCE_URL:{link}-->\n")
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
    parser.add_argument('--collection-name', required=True,
                       help='Collection name format with {state} placeholder')
    return parser.parse_args()

def get_directory_name(collection_name: str, state_code: str) -> str:
    """Generate directory name based on collection name format"""
    return f"websites-{collection_name.format(state=state_code.lower())}"

def run_wget_command(command: str, base_url: str) -> bool:
    """Execute wget command and return success status"""
    try:
        # Run wget command with --save-headers to preserve response headers
        # which include the final URL after any redirects
        modified_command = command.replace('wget', 'wget --save-headers')
        subprocess.run(modified_command, shell=True, check=True)
        
        # After wget completes, process downloaded files
        output_dir = command.split(' -P ')[1].split(' ')[0]  # Extract output directory
        for file in os.listdir(output_dir):
            if file.endswith(('.html', '.txt', '.tmp')):
                file_path = os.path.join(output_dir, file)
                try:
                    # Read current content with headers
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Extract the actual URL from wget headers
                    # wget saves the URL in a header like "Location: http://..."
                    actual_url = None
                    header_end = content.find('\n\n')  # Headers are separated from content by double newline
                    if header_end != -1:
                        headers = content[:header_end]
                        # Try to find the final URL from headers
                        for line in headers.split('\n'):
                            if line.startswith('Location: '):
                                actual_url = line[10:].strip()
                                break
                        # If no Location header, try to find the original URL
                            elif line.startswith('--'):  # wget request line
                                parts = line.split(' ')
                                if len(parts) > 1:
                                    actual_url = parts[1].strip()
                                    break
                        
                        # Remove headers from content
                        content = content[header_end + 2:]
                    
                    # If we couldn't find the URL in headers, construct it from the filename
                    if not actual_url:
                        # Remove common wget suffixes and construct URL
                        clean_filename = file.replace('.html', '').replace('.tmp', '').replace('.txt', '')
                        actual_url = f"{base_url.rstrip('/')}/{clean_filename}"
                    
                    # Write content back with the actual source URL
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(f"<!--SOURCE_URL:{actual_url}-->\n")
                        f.write(content)
                
                except Exception as e:
                    print(f"Warning: Error processing file {file}: {str(e)}")
                    continue
        
        print(f"✅ Successfully executed wget command: {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error executing wget command: {str(e)}")
        return False

def main():
    args = parse_args()
    
    # Special handling for NJ and OR using wget commands
    wget_commands = {
        'nj': (lambda dir_name: f'wget -r -np -nd -A.html,.txt,.tmp -P {dir_name} https://www.nj.gov/labor/myleavebenefits/',
               'https://www.nj.gov/labor/myleavebenefits/'),
        'or': (lambda dir_name: f'wget -r -np -nd -A.txt,.tmp -P {dir_name} https://paidleave.oregon.gov/',
               'https://paidleave.oregon.gov/')
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
                if not run_wget_command(wget_commands[state_lower][0](get_directory_name(args.collection_name, state)), wget_commands[state_lower][1]):
                    print(f"Failed to process {state.upper()} using wget")
                continue
            
            # Handle other states using existing method
            if state_lower in state_map:
                state_links.append(state_map[state_lower])
    
    driver = None
    try:
        for links, state_code in state_links:
            # Create state-specific directory if it doesn't exist
            directory = get_directory_name(args.collection_name, state_code)
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