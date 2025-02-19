import os
from bs4 import BeautifulSoup
import chardet
import argparse

import unicodedata

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--states', nargs='+', help='List of state codes to process')
    parser.add_argument('--collection-name', required=True,
                       help='Collection name format with {state} placeholder')
    return parser.parse_args()

def get_directory_names(collection_name: str, state: str) -> tuple:
    """Generate input and output directory names based on collection name format"""
    formatted_name = collection_name.format(state=state.lower())
    return (f"websites-{formatted_name}", f"cleaned_websites-{formatted_name}")

def get_state_dirs(states=None, collection_name=None):
    default_states = ["co", "ny", "ma", "ca", "wa", "ri", "dc", "ct", "nj", "or", "general"]
    states_to_process = states if states else default_states
    
    return [get_directory_names(collection_name, state) for state in states_to_process]

def get_unique_filename(output_file_path, extension=".txt"):
    counter = 1
    original_output_file_path = output_file_path
    while os.path.exists(output_file_path):
        output_file_path = original_output_file_path.replace(extension, f"_{counter}{extension}")
        counter += 1
    return output_file_path

def process_file(file_path, encoding):
    with open(file_path, 'r', encoding=encoding) as file:
        file_content = file.read()

    # Extract source URL if present
    source_url = None
    if "<!--SOURCE_URL:" in file_content:
        url_start = file_content.index("<!--SOURCE_URL:") + 14
        url_end = file_content.index("-->", url_start)
        source_url = file_content[url_start:url_end]
        # Remove the URL comment from content
        file_content = file_content[file_content.index("-->") + 3:]

    # Create a Beautiful Soup object and get clean text
    soup = BeautifulSoup(file_content, features="lxml")
    clean_text = soup.get_text(separator="\n", strip=True)
    normalized_text = unicodedata.normalize('NFKC', clean_text)

    return normalized_text, source_url

def clean_output_directory(output_dir):
    """Clean existing directory or create new one"""
    if os.path.exists(output_dir):
        # Remove all files in directory
        for file in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error: {e}")
    else:
        os.makedirs(output_dir)
    print(f"Cleaned/created directory: {output_dir}")

def main():
    args = parse_args()
    state_dirs = get_state_dirs(args.states, args.collection_name)
    
    # Process each state directory
    for input_dir, output_dir in state_dirs:
        if not os.path.exists(input_dir):
            print(f"Skipping {input_dir} - directory not found")
            continue
        
        print(f"\nProcessing {input_dir}...")
        
        # Clean output directory before processing
        clean_output_directory(output_dir)
        
        # Loop through all subdirectories and files in the directory
        for root, dirs, files in os.walk(input_dir, topdown=False):
            for filename in files:
                # Construct the full file path
                file_path = os.path.join(root, filename)

                # Check if the path is a file
                if os.path.isfile(file_path):
                    try:
                        # Detect the file's encoding using chardet
                        with open(file_path, 'rb') as file:
                            raw_data = file.read()
                            encoding = chardet.detect(raw_data)['encoding']

                        # Process the file
                        clean_text, source_url = process_file(file_path, encoding)

                        # Ensure the output directory exists
                        if not os.path.exists(output_dir):
                            os.makedirs(output_dir)

                        # Construct the output file path with .txt extension
                        output_file_path = os.path.join(output_dir, os.path.basename(filename).split(".")[0] + ".txt")

                        # Get a unique file name if the file already exists
                        output_file_path = get_unique_filename(output_file_path)

                        # Save both the clean text and source URL
                        with open(output_file_path, 'w', encoding='utf-8') as file:
                            if source_url:
                                file.write(f"SOURCE_URL: {source_url}\n---\n")
                            file.write(clean_text)

                        print(f"Cleaned: {file_path} -> {output_file_path}")

                    except UnicodeDecodeError:
                        print(f"Error decoding file: {file_path}")

    print("\nAll cleaning completed.")

if __name__ == "__main__":
    main()
