import os
from dotenv import load_dotenv

load_dotenv()

fernet_key = os.getenv("FERNET_KEY", "")

# VK
vk_api_key = os.getenv("VK_API_KEY", "")
vk_group_id = os.getenv("VK_GROUP_ID", "")