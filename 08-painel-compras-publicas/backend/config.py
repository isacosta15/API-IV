import os
from dotenv import load_dotenv
load_dotenv()
REQUEST_TIMEOUT=int(os.getenv('REQUEST_TIMEOUT','60'))
