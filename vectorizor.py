import jsonlines
from openai import OpenAI
import openai
from qdrant_client import QdrantClient
import time
# from ragas.llms.prompt import Prompt
from dotenv import load_dotenv  # Add this import
import os

# Load environment variables from .env file
load_dotenv()

openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Define the states to process
STATE_CODES = ["co", "ny", "ma", "ca", "wa", "ri", "dc", "ct", "nj", "or"]

# Load data from train.jsonl file
def load_data(file_path):
    data = []
    with jsonlines.open(file_path) as f:
        for item in f:
            data.append(item)
    return data

# Modified to handle multiple collections
def init_qdrant(collection_name):
    qclient = QdrantClient(host="localhost", port=6333)
    try:
        # Check if the collection exists, if not, create it
        qclient.create_collection(
            collection_name=collection_name,
            vectors_config={
                "size": 1536,
                "distance": "Cosine"
            }
        )
        print(f"Collection {collection_name} initialized")
    except Exception as e:
        print(f"Collection {collection_name} already exists")
    return qclient

# Create embeddings and populate Qdrant collection
def create_and_index_embeddings(data, model, client, collection_name):
    last_request_time = None
    request_interval = 0.5 
    batch_size = 32

    for start_index in range(0, len(data), batch_size):
        current_time = time.time()
        if last_request_time is not None:
            elapsed_time = current_time - last_request_time
            if elapsed_time < request_interval:
                time.sleep(request_interval - elapsed_time)

        text_batch = [item["text"] for item in data[start_index:start_index+batch_size]]
        try:
            res = openai_client.embeddings.create(input=text_batch, model=model)

            embeddings = [embedding.embedding for embedding in res.data]
            points = [{"id": start_index + i, "vector": embeddings[i], "payload": data[start_index + i]} for i in range(len(embeddings))]
            client.upsert(collection_name=collection_name, points=points)
            last_request_time = time.time()
        except openai.RateLimitError as e:
            print(f"Rate limit reached, waiting a bit longer...")
            time.sleep(5)  # rate limit 
            continue  # Retry the current batch

if __name__ == "__main__":
    MODEL = "text-embedding-ada-002"
    qdrant_client = init_qdrant("dummy")  # Initialize client once
    
    # Process each state's data
    for state in STATE_CODES:
        input_file = f"chunker-new-results/chunker-new-{state}.jsonl"
        collection_name = f"{state}-pfl-new-chunker-2025"
        
        print(f"\nProcessing state: {state}")
        print(f"Loading data from: {input_file}")
        
        try:
            # Load and process data for current state
            state_data = load_data(input_file)
            print(f"Loaded {len(state_data)} documents for {state}")
            
            # Create collection for current state
            init_qdrant(collection_name)
            
            # Create and index embeddings for current state
            create_and_index_embeddings(state_data, MODEL, qdrant_client, collection_name)
            print(f"Completed processing for {state}")
            
        except FileNotFoundError:
            print(f"File not found for state {state}, skipping...")
        except Exception as e:
            print(f"Error processing state {state}: {e}")
