import os
from dotenv import load_dotenv

load_dotenv()

RETELL_API_KEY = os.getenv('RETELL_API_KEY')
RETELL_AGENT_ID = os.getenv('RETELL_AGENT_ID')
RETELL_PHONE_NUMBER = os.getenv('RETELL_PHONE_NUMBER')