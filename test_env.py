from dotenv import load_dotenv
import os

load_dotenv()  # loads variables from .env

database_url = os.getenv("DATABASE_URL")
print("DATABASE_URL:", database_url)
