import os
from langchain.document_loaders import ReadTheDocsLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm.auto import tqdm
import hashlib
import json
import tiktoken
from textblob import TextBlob
from bs4 import BeautifulSoup


tokenizer = tiktoken.get_encoding('cl100k_base')

def clean_html(html_content):
    # Use Beautiful Soup to remove HTML tags
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    # Replace newline characters with a space
    cleaned_text = text.replace('\n', ' ')
    cleaned_text = cleaned_text.replace('\n\n', ' ')
    return cleaned_text


def tiktoken_len(text):
    tokens = tokenizer.encode(
        text,
        disallowed_special=()
    )
    return len(tokens)

def process_txt_files(folder_path):
    # Get all files in the folder
    all_files = os.listdir(folder_path)

    # Filter out HTML files
    txt_files = [file for file in all_files if file.endswith('.txt')]

    # Initialize tokenizer and text_splitter
    tokenizer = tiktoken.get_encoding('cl100k_base')
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=20,
        length_function=tiktoken_len,
        separators=['\n\n', '\n', ' ', '']
    )

    documents = []

    # Process each HTML file
    for txt_file in tqdm(txt_files):
        try:
            file_path = os.path.join(folder_path, txt_file)

            with open(file_path, 'r') as f:
                content = f.read()

            # Generate a unique ID based on the file path
            m = hashlib.md5()
            m.update(file_path.encode('utf-8'))
            uid = m.hexdigest()[:12]

            # Split the content into chunks
            chunks = text_splitter.split_text(content)

            # Create document data
            for i, chunk in enumerate(chunks):
                clean_chunk = clean_html(chunk)
                blob = TextBlob(clean_chunk)
                nounPhrases = blob.noun_phrases
                unique_nounPhrases = list(set(nounPhrases))
                
                topic = os.path.basename(file_path).replace('-', ' ').split('.')[0]
                
                documents.append({
                    'id': f'{uid}-{i}',
                    'text': clean_chunk,
                    'keywords': unique_nounPhrases,
                    'topic': topic
                })

            # Delete the HTML file after processing
            # os.remove(file_path)

        except Exception as e:
            print(f"Error processing file {txt_file}: {e}")

    # Save the documents to a JSONL file
    with open('train.jsonl', 'w') as f:
        for doc in documents:
            f.write(json.dumps(doc) + '\n')

    return documents

# Call the function with the folder path "websites"
folder_path = "cleaned_websites"
documents = process_txt_files(folder_path)