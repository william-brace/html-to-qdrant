# Project README

## Overview

This project consists of multiple components designed to download website content, clean and process the HTML content into textual data, segment the cleaned data into manageable chunks, and finally vectorize the textual data for indexing into a vector database using Qdrant. It's an end-to-end pipeline from data acquisition to preparation for advanced search and retrieval capabilities.

### Components

1. **Orchestrator (`orchestrator.py`)**: The main script that coordinates the entire pipeline. It sequentially runs:
   - `getHTML.py`: Downloads website content
   - `cleaner.py`: Cleans HTML into text
   - `chunker-new.py`: Segments text into chunks
   - `vectorizor.py`: Creates and stores embeddings

   The orchestrator can be configured to:
   - Process specific states (e.g., ["ny", "ca", "general"])
   - Overwrite existing vector collections
   - Handle errors and provide progress feedback

2. **Web Downloader (`getHTML.py`)**: Downloads website content using either direct links or wget commands:
   - Uses predefined links from `links.py` for most states
   - Uses wget commands for NJ and OR websites
   - Creates state-specific directories (e.g., `websites-ny`, `websites-ca`)

3. **Cleaner (`cleaner.py`)**: Processes the downloaded HTML files:
   - Removes HTML tags and extracts clean text
   - Handles different character encodings
   - Outputs to state-specific cleaned directories (e.g., `cleaned_websites-ny`)

4. **Chunker (`chunker-new.py`)**: The primary chunking implementation that:
   - Splits text into 500-character chunks with 50-character overlap
   - Extracts keywords using TextBlob
   - Generates unique IDs for each chunk
   - Saves results as JSONL files in `chunker-new-results` directory

5. **Vectorizer (`vectorizor.py`)**: Creates embeddings and manages Qdrant collections:
   - Uses OpenAI's embedding model
   - Creates state-specific collections in Qdrant
   - Supports overwriting or appending to existing collections

### Requirements

- Dependencies listed in `requirements.txt`
  
```bash
pip install -r requirements.txt
```

### Setup

1. **Install Dependencies**:
    - Ensure you have Python 3.x installed
    - Install required packages: `pip install -r requirements.txt`

2. **Environment Variables**:
    - Create a `.env` file in the project root
    - Add your OpenAI API key: `OPENAI_API_KEY=your_key_here`

3. **Running the Pipeline**

The pipeline can be run using either the orchestrator (recommended) or individual scripts. All scripts now use consistent command-line arguments.

#### Using the Orchestrator

The orchestrator requires two main arguments:
- `--states` or `--all`: Specify states to process
- `--collection-name`: Collection name format with {state} placeholder
- Optional: `--overwrite`: Flag to overwrite existing vector collections

Available states: "ny", "nj", "or", "co", "ct", "ca", "ma", "wa", "ri", "dc", "general"

Examples:
```bash
# Process specific states
python orchestrator.py --states ny ca wa --collection-name "{state}-pfl-2025"

# Process all available states
python orchestrator.py --all --collection-name "{state}-chunk-links"

# Process specific states and overwrite existing collections
python orchestrator.py --states ny nj --collection-name "{state}-pfl-data" --overwrite
```

#### Running Scripts Individually

Each script requires at minimum:
- `--states`: List of state codes to process
- `--collection-name`: Collection name format with {state} placeholder

1. **Download HTML (`getHTML.py`)**:
```bash
python getHTML.py --states ny ca --collection-name "{state}-pfl-2025"
```

2. **Clean HTML (`cleaner.py`)**:
```bash
python cleaner.py --states ny ca --collection-name "{state}-pfl-2025"
```

3. **Chunk Text (`chunker-new.py`)**:
```bash
python chunker-new.py --states ny ca --collection-name "{state}-pfl-2025"
```

4. **Vectorize Chunks (`vectorizor.py`)**:
```bash
# Without overwriting existing collections
python vectorizor.py --states ny ca --collection-name "{state}-pfl-2025"

# With overwriting existing collections
python vectorizor.py --states ny ca --collection-name "{state}-pfl-2025" --overwrite
```

### Directory Structure

The pipeline creates directories based on the collection name format:
```
project/
├── websites-{collection-name}/          # Raw downloaded HTML
├── cleaned_websites-{collection-name}/  # Cleaned text files
├── chunker-new-results/                 # Chunked JSONL files
│   └── chunks-{collection-name}.jsonl
└── vector_db/                           # Qdrant storage (default location)
```

For example, with `--collection-name "{state}-pfl-2025"`, you'll get:
```
websites-ny-pfl-2025/
cleaned_websites-ny-pfl-2025/
chunker-new-results/chunks-ny-pfl-2025.jsonl
```

### Legacy Components

The project includes alternative chunking implementations (`chunker.py`, `htmlChunker.py`, `gptChunker.py`, `slidingChunker.py`) that were used in earlier versions. While these remain available, the current pipeline uses `chunker-new.py`, which provides a balanced approach to text segmentation with keyword extraction.

### Notes

- The orchestrator provides the most streamlined way to run the entire pipeline
- Each script can still be run independently if needed
- Use the `--states` parameter to process specific states
- Use `--overwrite` with vectorizor.py to replace existing collections
- The general collection is named `general-pfl-new-chunker-2025`
- State-specific collections are named `{state}-pfl-new-chunker-2025`

