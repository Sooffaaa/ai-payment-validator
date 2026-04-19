from openai import OpenAI
from core.config import Config
import json
import re

class AIService:
    def __init__(self):
        self.client = OpenAI(
            base_url=Config.BASE_URL,
            api_key=Config.OPENROUTER_API_KEY
        )

    def extract_payment_data(self, text: str):
        try:
            response = self.client.chat.completions.create(
                model=Config.DEFAULT_MODEL,
                messages=[
                    {
                        "role": "system", 
                        "content": (
                            "You are a professional financial data extractor. "
                            "Extract details into a valid JSON object. "
                            "Format: {\"amount\": float, \"currency\": \"string\", \"address\": \"string\"}. "
                            "Rules: "
                            "1. Output ONLY JSON. "
                            "2. No markdown blocks (no ```json). "
                            "3. Use double quotes for keys and values. "
                            "4. If data is missing, use null."
                        )
                    },
                    {
                        "role": "user", 
                        "content": f"Example: 'Send 100 USD to 0x123' -> {{\"amount\": 100.0, \"currency\": \"USD\", \"address\": \"0x123\"}}. "
                                   f"Now parse this text: {text}"
                    }
                ],
                temperature=0.1,
            )

            raw_content = response.choices[0].message.content

            match = re.search(r'\{.*\}', raw_content, re.DOTALL)
            if not match:
                raise Exception(f"JSON не найден в ответе ИИ. Ответ: {raw_content[:50]}...")
            
            clean_json = match.group(0)

            clean_json = clean_json.replace("```json", "").replace("```", "").strip()

            clean_json = clean_json.replace("'", '"')

            clean_json = re.sub(r',\s*}', '}', clean_json)

            return json.loads(clean_json)

        except json.JSONDecodeError as e:
            raise Exception(f"Ошибка формата JSON: {str(e)}. ИИ прислал: {clean_json[:100]}")
        except Exception as e:
            raise Exception(f"Сбой сервиса AI: {str(e)}")
