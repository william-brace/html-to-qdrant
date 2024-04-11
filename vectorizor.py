import jsonlines
from openai import OpenAI
import openai
from qdrant_client import QdrantClient
import time

openai_client = OpenAI()

COLLECTION_NAME = "ct-pfl"

# Load data from train.jsonl file
def load_data(file_path):
    data = []
    with jsonlines.open(file_path) as f:
        for item in f:
            data.append(item)
    return data

# Initialize Qdrant Client and Collection
def init_qdrant( collection_name):
    qclient = QdrantClient(host="localhost", port=6333)
    # Check if the collection exists, if not, create it
    qclient.create_collection(
    collection_name=collection_name,
    vectors_config={
        "size": 1536, 
        "distance": "Cosine"  
    }
)
    return qclient, collection_name

# Create embeddings and populate Qdrant collection
def create_and_index_embeddings(data, model, client, collection_name):
    last_request_time = None
    request_interval = 0.5  # Adjust based on your calculations
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
            # Adjusted line to correctly access embeddings
            embeddings = [embedding.embedding for embedding in res.data]
            points = [{"id": start_index + i, "vector": embeddings[i], "payload": data[start_index + i]} for i in range(len(embeddings))]
            client.upsert(collection_name=collection_name, points=points)
            last_request_time = time.time()
        except openai.RateLimitError as e:
            print(f"Rate limit reached, waiting a bit longer...")
            time.sleep(5)  # Wait a bit longer if rate limit is reached
            continue  # Retry the current batch

if __name__ == "__main__":
    train_data = load_data("train.jsonl")
    MODEL = "text-embedding-ada-002"
    qdrant_client, collection_name = init_qdrant(COLLECTION_NAME)
    create_and_index_embeddings(train_data, MODEL, qdrant_client, collection_name)
