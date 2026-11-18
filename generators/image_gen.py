from openai import (
    OpenAI,
    APIError,
    APIConnectionError,
    RateLimitError,
    AuthenticationError
)

class ImageGenerator:
    def __init__(self, openai_key):
        self.client = OpenAI(api_key=openai_key)

    def generate_image(self, prompt):
        try:
            response = self.client.images.generate(
                model="gpt-image-2.5-flare",
                prompt=prompt,
                size="1024x1024",
                quality="low",
                n=1,
            )

            image_url = response.data[0].url
            return image_url

        except AuthenticationError:
            raise Exception("Ошибка авторизации OpenAI. Проверьте API-ключ.")

        except RateLimitError:
            raise Exception("Превышен лимит запросов или недостаточно средств на балансе OpenAI.")

        except APIConnectionError:
            raise Exception("Не удалось подключиться к OpenAI. Проверьте интернет-соединение.")

        except APIError as e:
            raise Exception(f"Ошибка OpenAI API: {e}")
