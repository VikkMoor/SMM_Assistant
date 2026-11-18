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

    def upload_photo(self, image_url):
        try:
            upload_url_response = requests.get(
                'https://api.vk.com/method/photos.getWallUploadServer',
                params={
                    'access_token': self.vk_api_key,
                    'v': '5.236',
                    'group_id': self.group_id
                },
                timeout=15
            ).json()

        except RequestException as e:
            self.handle_request_error(e)

        upload_url_response = self.check_vk_error(upload_url_response)

        upload_url = upload_url_response['response']['upload_url']

        try:
            image_response = requests.get(image_url, timeout=15)
            image_response.raise_for_status()
            image_data = image_response.content

        except RequestException as e:
            self.handle_request_error(e)

        try:
            upload_response = requests.post(
                upload_url,
                files={'photo': ('image.jpg', image_data)},
                timeout=15
            ).json()

        except RequestException as e:
            self.handle_request_error(e)

        # Проверяем ответ сервера загрузки
        if not all(key in upload_response for key in ('photo', 'server', 'hash')):
            raise Exception('Ошибка загрузки фотографии на сервер VK.')


        try:
            save_response = requests.get(
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
            ).json()

        except RequestException as e:
            self.handle_request_error(e)

        save_response = self.check_vk_error(save_response)

        photo_id = save_response['response'][0]['id']
        owner_id = save_response['response'][0]['owner_id']

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
