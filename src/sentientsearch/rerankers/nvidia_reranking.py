import os
import requests
from dotenv import load_dotenv

# Constants
load_dotenv()  # Load environment variables
NVIDIA_API_KEY = os.getenv('NVIDIA_API_KEY')
NVIDIA_API_URL = "http://localhost:8002/v1/ranking"
#"https://ai.api.nvidia.com/v1/retrieval/nvidia/reranking"
MODEL = "nvidia/nv-rerankqa-mistral-4b-v3"
#"nvidia/rerank-qa-mistral-4b"

def get_reranking_nvidia(docs, query, top_res=None):
    """
    Re-ranks a list of documents based on a query using NVIDIA's reranking API.

    Args:
    docs (list of str): List of documents to be re-ranked.
    query (str): Query string to rank the documents against.
    top_res (int, optional): Number of top results to return. If None, returns all results.

    Returns:
    list of str: Re-ranked documents based on the query.
    """
    try:
        # Prepare the payload
        payload = {
            "model": MODEL,
            "query": {"text": query},
            "passages": [{"text": doc} for doc in docs],
        }
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            # "Authorization": f"Bearer {NVIDIA_API_KEY}"
        }

        # Make the API call
        response = requests.post(NVIDIA_API_URL, json=payload, headers=headers)
        response.raise_for_status()  # Raise exception for bad status codes
        
        results = response.json()
        
        # Get the rankings and sort documents accordingly
        rankings = results.get("rankings", [])
        ranked_docs = []
        for rank in rankings:
            doc_index = rank["index"]
            if doc_index < len(docs):  # Safety check
                ranked_docs.append(docs[doc_index])
        
        # Return top_res results if specified, otherwise return all
        if top_res:
            return ranked_docs[:top_res]
        return ranked_docs

    except Exception as e:
        print(f"An error occurred: {e}")
        return []