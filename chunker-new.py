import os
from langchain.text_splitter import RecursiveCharacterTextSplitter, TokenTextSplitter
from tqdm.auto import tqdm
import hashlib
import json
from textblob import TextBlob
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--states', nargs='+', help='List of state codes to process')
    parser.add_argument('--collection-name', required=True,
                       help='Collection name format with {state} placeholder')
    return parser.parse_args()

def get_directory_names(collection_name: str, state: str) -> tuple:
    """Generate input directory and results filename based on collection name format"""
    formatted_name = collection_name.format(state=state.lower())
    return (f"cleaned_websites-{formatted_name}", f"chunks-{formatted_name}.jsonl")

def get_state_dirs(states=None, collection_name=None):
    default_states = ["co", "ny", "ma", "ca", "wa", "ri", "dc", "ct", "nj", "or", "general"]
    states_to_process = states if states else default_states
    
    return [get_directory_names(collection_name, state) for state in states_to_process]

# Initialize the text splitter with a chunk size of 4000 tokens and an overlap of 200 tokens
text_splitter = TokenTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

def process_state_files(folder_path):
    try:
        print(f"Processing files in folder: {folder_path}")
        all_files = os.listdir(folder_path)
        text_files = [file for file in all_files if file.endswith('.txt')]
        print(f"Found {len(text_files)} text files.")

        documents = []
        for text_file in tqdm(text_files):
            try:
                file_path = os.path.join(folder_path, text_file)
                print(f"Processing file: {file_path}")
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Extract source URL if present
                source_url = None
                if content.startswith("SOURCE_URL: "):
                    url_end = content.index("\n")
                    source_url = content[11:url_end].strip()
                    content = content[content.index("---\n") + 4:]
                
                # Split the text into chunks
                chunks = text_splitter.split_text(content)
                
                # Create documents with metadata for each chunk
                for i, chunk in enumerate(chunks):
                    # Create TextBlob for keyword extraction
                    blob = TextBlob(chunk)
                    noun_phrases = blob.noun_phrases
                    unique_noun_phrases = list(set(noun_phrases))
                    
                    # Include source URL in metadata
                    document = {
                        'id': f"{hashlib.md5(file_path.encode('utf-8')).hexdigest()[:12]}-{i}",
                        'text': chunk,
                        'metadata': {
                            'keywords': unique_noun_phrases,
                            'source_url': source_url
                        }
                    }
                    documents.append(document)
                
                print(f"File {text_file} processed successfully.")
            except Exception as e:
                print(f"Error processing file {text_file}: {e}")
        
        return documents
    except Exception as e:
        print(f"Error processing directory: {e}")
        return []

def clean_results_directory(results_dir):
    """Clean existing results directory or create new one"""
    if os.path.exists(results_dir):
        # Remove all files in directory
        for file in os.listdir(results_dir):
            file_path = os.path.join(results_dir, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error: {e}")
    else:
        os.makedirs(results_dir)
    print(f"Cleaned/created directory: {results_dir}")

def process_all_states(state_dirs):
    try:
        print("Starting to process all state directories...")
        
        # Clean/create results directory
        results_dir = "chunker-new-results"
        clean_results_directory(results_dir)
        
        for input_dir, result_filename in state_dirs:
            if not os.path.exists(input_dir):
                print(f"Skipping {input_dir} - directory not found")
                continue
                
            print(f"\nProcessing directory: {input_dir}")
            state_documents = process_state_files(input_dir)
            
            # Save state-specific documents
            output_file = os.path.join(results_dir, result_filename)
            with open(output_file, 'w') as f:
                for doc in state_documents:
                    f.write(json.dumps(doc) + '\n')
            print(f"Saved {len(state_documents)} documents to {output_file}")
            
        print("\nAll states processed.")
    except Exception as e:
        print(f"Error processing states: {e}")

def main():
    args = parse_args()
    state_dirs = get_state_dirs(args.states, args.collection_name)
    process_all_states(state_dirs)

if __name__ == "__main__":
    main()