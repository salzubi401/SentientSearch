from src.sentientsearch.main import ask
import nest_asyncio
import asyncio
import json
from datetime import datetime

class SentientSearchQA:
    def __init__(self, pro_mode=False):
        # Initialize nest_asyncio for jupyter compatibility
        nest_asyncio.apply()
        self.date = datetime.now().strftime("%Y-%m-%d")
        self.location = "us"
        self.pro_mode = pro_mode

    async def _read_stream(self, response):
        """Helper method to read streaming response"""
        text = ""
        async for chunk in response.body_iterator:
            if isinstance(chunk, bytes):
                text += chunk.decode()
            else:
                text += chunk
        return text

    def _get_answer_text(self, response):
        """Helper method to extract answer text from response"""
        lines = response.split('\n')
        answer = []
        for line in lines:
            if line:
                if line.startswith('data:'):
                    try:
                        data = json.loads(line[5:])
                        if data['type'] == 'llm':
                            answer.append(data['text'])
                    except:
                        pass
        return ''.join(answer)

    async def chat_completion_async(self, query):
        """
        Main method to get chat completions
        
        Args:
            query (str): The question to ask
            date (str): Target date in YYYY-MM-DD format
            language (str): Language code (e.g. 'jp')
            debug (bool): Debug mode flag
            
        Returns:
            str: The processed answer text
        """
        response = ask(query, self.date, self.location, self.pro_mode)
        raw_text = await self._read_stream(response)
        return self._get_answer_text(raw_text)

    def chat_completion(self, query):
        """Synchronous wrapper for chat_completion"""
        return asyncio.run(self.chat_completion_async(query))
