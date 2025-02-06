import os
from bs4 import BeautifulSoup
import chardet

import unicodedata

def get_unique_filename(output_file_path, extension=".txt"):
    counter = 1
    original_output_file_path = output_file_path
    while os.path.exists(output_file_path):
        output_file_path = original_output_file_path.replace(extension, f"_{counter}{extension}")
        counter += 1
    return output_file_path

# Define the state directories to process
state_dirs = [
    ("websites-co", "cleaned_websites-co"),
    ("websites-ny", "cleaned_websites-ny"),
    ("websites-ma", "cleaned_websites-ma"),
    ("websites-ca", "cleaned_websites-ca"),
    ("websites-wa", "cleaned_websites-wa"),
    ("websites-ri", "cleaned_websites-ri"),
    ("websites-dc", "cleaned_websites-dc"),
    ("websites-ct", "cleaned_websites-ct"),
    ("websites-nj", "cleaned_websites-nj"),
    ("websites-or", "cleaned_websites-or")
]

# Process each state directory
for input_dir, output_dir in state_dirs:
    if not os.path.exists(input_dir):
        print(f"Skipping {input_dir} - directory not found")
        continue
        
    print(f"\nProcessing {input_dir}...")
    
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

                    # Read the file content with the detected encoding
                    with open(file_path, 'r', encoding=encoding) as file:
                        file_content = file.read()

                    # Create a Beautiful Soup object and get clean text
                    soup = BeautifulSoup(file_content, features="lxml")
                    clean_text = soup.get_text(separator="\n", strip=True)
                    normalized_text = unicodedata.normalize('NFKC', clean_text)

                    # Ensure the output directory exists
                    if not os.path.exists(output_dir):
                        os.makedirs(output_dir)

                    # Construct the output file path with .txt extension
                    output_file_path = os.path.join(output_dir, os.path.basename(filename).split(".")[0] + ".txt")

                    # Get a unique file name if the file already exists
                    output_file_path = get_unique_filename(output_file_path)

                    # Save the clean text to a file in UTF-8
                    with open(output_file_path, 'w', encoding='utf-8') as file:
                        file.write(clean_text)

                    print(f"Cleaned: {file_path} -> {output_file_path}")

                except UnicodeDecodeError:
                    print(f"Error decoding file: {file_path}")

print("\nAll cleaning completed.")
