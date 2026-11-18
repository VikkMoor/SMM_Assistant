from openai import OpenAI, APIError, APIConnectionError, RateLimitError, AuthenticationError

class PostGenerator:
    def __init__(self, openai_key, tone, topic):
        self.client = OpenAI(api_key=openai_key)
        self.tone = tone
        self.topic = topic


    def generate_post(self):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "Ты профессиональный SMM-специалист. Создавай интересные, оригинальные и грамотные публикации для социальных сетей. Учитывай заданную тему и тон общения. Избегай шаблонных фраз и неуместных хэштегов."
                    },
                    {
                        "role": "user",
                        "content": f"Сгенерируй пост для соцсетей с темой {self.topic}, используя тон: {self.tone}"
                    }
                ]
            )

            return response.choices[0].message.content

        except AuthenticationError:
            raise Exception("Ошибка авторизации OpenAI. Проверьте API-ключ.")

        except RateLimitError:
            raise Exception("Превышен лимит запросов или недостаточно средств на балансе OpenAI.")

        except APIConnectionError:
            raise Exception("Не удалось подключиться к OpenAI. Проверьте интернет-соединение.")

        except APIError as e:
            raise Exception(f"Ошибка OpenAI API: {e}")

    def generate_post_image_description(self):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "Ты профессиональный специалист по созданию промптов для генерации изображений. Составляй подробные и понятные описания изображений на основе заданной темы. Указывай основные объекты, композицию, освещение, цветовую гамму и визуальный стиль. Не добавляй текст и надписи на изображение, если об этом отдельно не попросили."
                    },
                    {
                        "role": "user",
                        "content": f"Составь промпт для генерации изображения для публикации в соцсетях на тему: {self.topic}"
                    }
                ]
            )

            return response.choices[0].message.content

        except AuthenticationError:
            raise Exception("Ошибка авторизации OpenAI. Проверьте API-ключ.")

        except RateLimitError:
            raise Exception("Превышен лимит запросов или недостаточно средств на балансе OpenAI.")

        except APIConnectionError:
            raise Exception("Не удалось подключиться к OpenAI. Проверьте интернет-соединение.")

        except APIError as e:
            raise Exception(f"Ошибка OpenAI API: {e}")
