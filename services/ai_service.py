from openai import OpenAI
from core.config import Config
import json
import re


class AIService:
    def __init__(self):
        Config.validate()

        self.client = OpenAI(
            base_url=Config.BASE_URL,
            api_key=Config.OPENROUTER_API_KEY,
            default_headers={
                "HTTP-Referer": Config.SITE_URL,
                "X-Title": Config.SITE_NAME,
            }
        )

    def extract_payment_data(self, text: str) -> dict:
        last_error = None

        for model in Config.DEFAULT_MODELS:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Ты парсер финансовых данных. "
                                "Извлеки и верни строго JSON с полями:\n"
                                "- amount (число)\n"
                                "- currency (строка)\n"
                                "- address (строка)\n\n"
                                "Без объяснений. Только JSON."
                            )
                        },
                        {"role": "user", "content": text}
                    ],
                    response_format={"type": "json_object"},
                )

                content = response.choices[0].message.content

                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return self._extract_json_fallback(content)

            except Exception as e:
                last_error = e
                continue

        raise Exception(f"Все модели недоступны. Последняя ошибка: {last_error}")

    def _extract_json_fallback(self, text: str) -> dict:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError("Не удалось извлечь JSON из ответа модели")