from openai import AsyncOpenAI
from config import LM_STUDIO_URL, LM_STUDIO_API_KEY, SYSTEM_PROMPT

class LLMClient:
    def __init__(self):
        self.client = AsyncOpenAI(base_url=LM_STUDIO_URL, api_key=LM_STUDIO_API_KEY)
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]

    async def get_response(self, user_text):
        """
        Get response from LM Studio.
        """
        self.history.append({"role": "user", "content": user_text})
        
        try:
            response = await self.client.chat.completions.create(
                model="local-model", # Model name is usually ignored by LM Studio
                messages=self.history,
                temperature=0.7,
            )
            
            reply = response.choices[0].message.content
            self.history.append({"role": "assistant", "content": reply})
            return reply
        except Exception as e:
            print(f"Error getting response from LLM: {e}")
            return "Sorry, I am having trouble thinking right now."
