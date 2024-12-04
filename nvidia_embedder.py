import os
from typing import Any, List, Optional

import requests
from pydantic import PrivateAttr

from encoder_base import DenseEncoder

class NvidiaEncoder(DenseEncoder):
    _client: Any = PrivateAttr()
    type: str = "nvidia"
    input_type: Optional[str] = "passage"
    url: Optional[str] = None

    def __init__(
        self,
        name: Optional[str] = "nvidia/nv-embedqa-e5-v5",
        nvidia_api_key: Optional[str] = None,
        score_threshold: float = 0.3,
        input_type: Optional[str] = "passage",
        url: Optional[str] = "https://integrate.api.nvidia.com/v1/embeddings",
    ):
        super().__init__(
            name=name,
            score_threshold=score_threshold,
            input_type=input_type,  # type: ignore
        )
        self.input_type = input_type
        self._client = self._initialize_client(nvidia_api_key)
        self.url = url
        
    def _initialize_client(self, nvidia_api_key: Optional[str] = None):
        """Initializes the NVIDIA client.

        :param nvidia_api_key: The API key for the NVIDIA client, can also
        be set via the NVIDIA_API_KEY environment variable.

        :return: The API key for use in requests.
        """
        nvidia_api_key = nvidia_api_key or os.getenv("NVIDIA_API_KEY")
        if nvidia_api_key is None:
            raise ValueError("NVIDIA API key cannot be 'None'.")
        return nvidia_api_key

    def __call__(self, docs: List[str]) -> List[List[float]]:
        if self._client is None:
            raise ValueError("NVIDIA client is not initialized.")
        try:
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "authorization": f"Bearer {self._client}"
            }
            payload = {
                "input": docs,
                "model": self.name,
                "input_type": self.input_type,
            }
            response = requests.post(self.url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json().get("data", [])
            embeddings = [item.get("embedding", []) for item in data]
            return embeddings
        except Exception as e:
            raise ValueError(f"NVIDIA API call failed. Error: {e}") from e
