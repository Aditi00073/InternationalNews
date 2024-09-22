import importlib
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    app_api = importlib.import_module("query")  # Keep it lowercase
    app_api.run()  # Call the run function in query.py
