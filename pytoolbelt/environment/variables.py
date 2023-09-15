import os
from dotenv import load_dotenv

load_dotenv()

PYTOOLBELT_DEBUG = os.environ.get("PYTOOLBELT_DEBUG", "").lower() == "true"
