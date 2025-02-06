import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm.auto import tqdm
import hashlib
import json
from textblob import TextBlob

# Define the state directories to process
state_dirs = [
    "cleaned_websites-co",
    "cleaned_websites-ny",
    "cleaned_websites-ma",
    "cleaned_websites-ca",
    "cleaned_websites-wa",
    "cleaned_websites-ri",
    "cleaned_websites-dc",
    "cleaned_websites-ct",
    "cleaned_websites-nj",
    "cleaned_websites-or"
]

# Initialize the text splitter with a chunk size of 500 characters and an overlap of 50 characters
text_splitter = RecursiveCharacterTextSplitter(
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
                
                # Split the text into chunks
                chunks = text_splitter.split_text(content)
                
                # Create documents with metadata for each chunk
                for i, chunk in enumerate(chunks):
                    # Create TextBlob for keyword extraction
                    blob = TextBlob(chunk)
                    noun_phrases = blob.noun_phrases
                    unique_noun_phrases = list(set(noun_phrases))
                    
                    # Create document with metadata
                    document = {
                        'id': f"{hashlib.md5(file_path.encode('utf-8')).hexdigest()[:12]}-{i}",
                        'text': chunk,
                        'metadata': {
                            'keywords': unique_noun_phrases
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

def process_all_states():
    try:
        print("Starting to process all state directories...")
        
        # Create results directory if it doesn't exist
        results_dir = "chunker-new-results"
        os.makedirs(results_dir, exist_ok=True)
        
        for state_dir in state_dirs:
            if not os.path.exists(state_dir):
                print(f"Skipping {state_dir} - directory not found")
                continue
                
            print(f"\nProcessing state directory: {state_dir}")
            state_documents = process_state_files(state_dir)
            
            # Get state name from directory
            state_name = state_dir.split('-')[1]
            
            # Save state-specific documents in the results directory
            output_file = os.path.join(results_dir, f'chunker-new-{state_name}.jsonl')
            with open(output_file, 'w') as f:
                for doc in state_documents:
                    f.write(json.dumps(doc) + '\n')
            print(f"Saved {len(state_documents)} documents to {output_file}")
            
        print("\nAll states processed.")
    except Exception as e:
        print(f"Error processing states: {e}")

# Process all states
process_all_states()