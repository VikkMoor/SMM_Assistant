import requests
from requests.exceptions import RequestException


class VKPublisher:
    def __init__(self, vk_api_key, group_id):
        self.vk_api_key = vk_api_key
        self.group_id = group_id

    def check_vk_error(self, response):
        if 'error' in response:
            raise Exception(response['error']['error_msg'])

        return response

    def handle_request_error(self, error):
        raise Exception(f"Ошибка сетевого запроса: {error}")

    def get_json_response(self, response, step):
        try:
            response.raise_for_status()
        except RequestException as e:
            raise Exception(f"{step}: ошибка HTTP-запроса: {e}")

        try:
            data = response.json()
        except ValueError:
            raise Exception(
                f"{step}: сервер вернул не JSON. "
                f"HTTP {response.status_code}. "
                f"Ответ: {response.text[:300]}"
            )

        return data

    def upload_photo(self, image_path):
        # Шаг 1. Получаем адрес сервера загрузки
        try:
            response = requests.get(
                'https://api.vk.com/method/photos.getWallUploadServer',
                params={
                    'access_token': self.vk_api_key,
                    'v': '5.236',
                    'group_id': self.group_id
                },
                timeout=15
            )
        except RequestException as e:
            self.handle_request_error(e)

        upload_url_response = self.get_json_response(
            response,
            'Получение сервера загрузки'
        )

        upload_url_response = self.check_vk_error(upload_url_response)

        upload_url = upload_url_response.get('response', {}).get('upload_url')

        if not upload_url:
            raise Exception('VK не вернул адрес сервера загрузки фотографии.')

        # Шаг 2. Загружаем локальный файл
        try:
            with open(image_path, 'rb') as image_file:
                response = requests.post(
                    upload_url,
                    files={
                        'photo': ('image.png', image_file, 'image/png')
                    },
                    timeout=30
                )
        except RequestException as e:
            self.handle_request_error(e)
        except OSError as e:
            raise Exception(f"Не удалось открыть изображение: {e}")

        upload_response = self.get_json_response(
            response,
            'Загрузка изображения на сервер VK'
        )

        # Проверяем значения, а не только наличие ключей
        required_fields = ('photo', 'server', 'hash')

        for field in required_fields:
            if upload_response.get(field) in (None, ''):
                raise Exception(
                    f"VK не вернул корректное значение поля '{field}'."
                )

        # Шаг 3. Сохраняем фотографию в VK
        try:
            response = requests.get(
                'https://api.vk.com/method/photos.saveWallPhoto',
                params={
                    'access_token': self.vk_api_key,
                    'v': '5.236',
                    'group_id': self.group_id,
                    'photo': upload_response['photo'],
                    'server': upload_response['server'],
                    'hash': upload_response['hash']
                },
                timeout=15
            )
        except RequestException as e:
            self.handle_request_error(e)

        save_response = self.get_json_response(
            response,
            'Сохранение фотографии в VK'
        )

        save_response = self.check_vk_error(save_response)

        photos = save_response.get('response')

        if not photos:
            raise Exception('VK не вернул сохранённую фотографию.')

        photo_id = photos[0].get('id')
        owner_id = photos[0].get('owner_id')

        if not photo_id or owner_id is None:
            raise Exception('VK вернул некорректные данные фотографии.')

        return f'photo{owner_id}_{photo_id}'

    def publish_post(self, content, image_url=None):
        params = {
            'access_token': self.vk_api_key,
            'from_group': 1,
            'v': '5.236',
            'owner_id': f'-{self.group_id}',
            'message': content
        }
        if image_url:
            attachment = self.upload_photo(image_url)
            params['attachments'] = attachment

        try:
            response = requests.post(
                'https://api.vk.com/method/wall.post',
                params=params,
                timeout=15
            ).json()

        except RequestException as e:
            self.handle_request_error(e)

        response = self.check_vk_error(response)

        return response
