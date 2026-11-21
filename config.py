import os
from dotenv import load_dotenv

load_dotenv()

fernet_key = os.getenv("FERNET_KEY", "")