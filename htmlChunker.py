import os
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_text_splitters import HTMLHeaderTextSplitter
from bs4 import BeautifulSoup
from textblob import TextBlob

def clean_html(html_content):
    # Use Beautiful Soup to remove HTML tags
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    cleaned_text = text.replace('\n', ' ')
    cleaned_text = cleaned_text.replace('\n\n', ' ')
    return cleaned_text

def process_html_files(folder_path):
    all_files = os.listdir(folder_path)
    # Filter out HTML files
    html_files = [file for file in all_files if file.endswith('.html')]

    documents = []
    headers_to_split_on = [
        ("h1", "Header 1"),
        ("h2", "Header 2"),
        ("h3", "Header 3"),
        ("h4", "Header 4"),
        ("h5", "Header 5"),
        ("h6", "Header 6"),
        ("p", "Paragraph"),
        ("ul", "Unordered List"),
        ("ol", "Ordered List"),
        ("blockquote", "Blockquote"),
        ("pre", "Preformatted Text"),
        ("code", "Code"),
        ("table", "Table"),
        ("div", "Division"),
        ("section", "Section"),
        ("article", "Article"),
        ("header", "Header"),
        ("footer", "Footer"),
        ("nav", "Navigation"),
        ("aside", "Aside"),
        ("main", "Main Content")
    ]
    html_splitter = HTMLHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    chunk_size = 500
    chunk_overlap = 30
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    for html_file in html_files:
        file_path = os.path.join(folder_path, html_file)
        with open(file_path, 'r') as f:
            content = f.read()

        html_header_splits = html_splitter.split_text(content)
        for split in html_header_splits:
            clean_content = clean_html(split.page_content)
            chunks = text_splitter.split_text(clean_content)

            for i, chunk in enumerate(chunks):
                blob = TextBlob(chunk)
                noun_phrases = blob.noun_phrases
                unique_noun_phrases = list(set(noun_phrases))
                topic = os.path.basename(file_path).replace('-', ' ').split('.')[0]

                documents.append({
                    'text': chunk,
                    'keywords': unique_noun_phrases,
                    'topic': topic,
                    'metadata': split.metadata
                })

    # Save the documents to a JSONL file
    with open('train.jsonl', 'w') as f:
        for doc in documents:
            f.write(json.dumps(doc) + '\n')

    return documents

if __name__ == "__main__":
    folder_path = "websites"
    documents = process_html_files(folder_path)
    print(documents)