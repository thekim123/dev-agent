import asyncio
import json


class LLMClient:
    def __init__(self, invoke_model, model_id):
        self.invoke_model = invoke_model
        self.model_id = model_id

    async def query_to_llm(self, prompt: str) -> str:
        body = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"text": prompt}
                    ]
                }
            ]
        }

        response = await asyncio.to_thread(
            self.invoke_model,
            modelId=self.model_id,
            body=json.dumps(body)
        )
        response_body = json.loads(response["body"].read())
        return response_body["output"]["message"]["content"][0]["text"]
