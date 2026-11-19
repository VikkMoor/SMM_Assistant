
import base64
import uuid
from pathlib import Path

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

            image_base64 = response.data[0].b64_json

            if not image_base64:
                raise Exception("OpenAI не вернул данные изображения.")

            image_data = base64.b64decode(image_base64)

            # Папка для сгенерированных изображений
            output_dir = (
                Path(__file__).resolve().parent.parent
                / "app"
                / "static"
                / "generated"
            )

            output_dir.mkdir(parents=True, exist_ok=True)

            # Создаём уникальное имя файла
            filename = f"{uuid.uuid4().hex}.png"
            image_path = output_dir / filename

            # Сохраняем изображение
            image_path.write_bytes(image_data)

            return str(image_path)

        except AuthenticationError:
            raise Exception("Ошибка авторизации OpenAI. Проверьте API-ключ.")

        except RateLimitError:
            raise Exception("Превышен лимит запросов или недостаточно средств на балансе OpenAI.")

        except APIConnectionError:
            raise Exception("Не удалось подключиться к OpenAI. Проверьте интернет-соединение.")

        except APIError as e:
            raise Exception(f"Ошибка OpenAI API: {e}")
