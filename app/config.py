import os
from dotenv import load_dotenv
from pathlib import Path


env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
