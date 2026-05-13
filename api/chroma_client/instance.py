from pathlib import Path

from api.chroma_client.chroma_client import ChromaClient

chroma_client = ChromaClient(vector_store_path=Path("vector_store"))
