import requests
import datetime

class VKStats:
    def __init__(self, vk_api_key, group_id):
        self.vk_api_key = vk_api_key
        self.group_id = group_id

    def get_stats(self, start_date, end_date):
        url = 'https://api.vk.com/method/stats.get'

        start_date = datetime.datetime.strptime(
            start_date, "%Y-%m-%d"
        ).replace(tzinfo=datetime.timezone.utc)

        end_date = datetime.datetime.strptime(
            end_date, "%Y-%m-%d"
        ).replace(
            hour=23,
            minute=59,
            second=59,
            tzinfo=datetime.timezone.utc
        )

        params = {
            'access_token': self.vk_api_key,
            'v': '5.236',
            'group_id': self.group_id,
            'timestamp_from': int(start_date.timestamp()),
            'timestamp_to': int(end_date.timestamp())
        }

        response = requests.get(url, params=params, timeout=15).json()

        if 'error' in response:
            raise Exception(response['error']['error_msg'])

        return response['response'][0]

    def get_followers(self):
        url = 'https://api.vk.com/method/groups.getMembers'

        params = {
            'access_token': self.vk_api_key,
            'v': '5.236',
            'group_id': self.group_id
        }

        response = requests.get(url, params=params, timeout=15).json()

        if 'error' in response:
            raise Exception(response['error']['error_msg'])

        return response['response']['count']


    def get_posts_stats(self):
        url = 'https://api.vk.com/method/wall.get'

        params = {
            'access_token': self.vk_api_key,
            'v': '5.236',
            'owner_id': -int(self.group_id),
            'count': 100,
            'filter': 'owner'
        }

        response = requests.get(url, params=params, timeout=15).json()

        if 'error' in response:
            raise Exception(response['error']['error_msg'])

        posts = response['response']['items']

        total_likes = 0
        total_reposts = 0

        for post in posts:
            total_likes += post.get('likes', {}).get('count', 0)
            total_reposts += post.get('reposts', {}).get('count', 0)

        return {
            'likes': total_likes,
            'reposts': total_reposts
        }

