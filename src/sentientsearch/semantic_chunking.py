import os

from semantic_chunkers import StatisticalChunker    
from src.sentientsearch.embedders.nvidia_embedder import NvidiaEncoder

#Implemented my own encoder
encoder = NvidiaEncoder(input_type='query')
#TODO: This chunker does not work well with weird characters...
chunker = StatisticalChunker(encoder=encoder, max_split_tokens=150)


def get_chunking(text):
    """
    Splits the provided text into meaningful chunks using a predefined chunker.

    Args:
    text (str): The text to be chunked.

    Returns:
    list: A list of chunks if the text is sufficiently long and non-empty; otherwise, an empty list.
    """
    try:
        chunks = chunker(docs=[text])
        values = [c.content for chunk in chunks for c in chunk]

        return values

    except Exception as e:
        print(f"Error during chunking process: {e}")
        return []
