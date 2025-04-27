import os
from dotenv import load_dotenv

def load_config():
    dotenv_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
    load_dotenv(dotenv_path=dotenv_path)

def check_env_vars():
    required_vars = ["MONGO_URI", "USE_GOOGLE_SHEETS", "CSV_PATH"]
    if os.getenv("USE_GOOGLE_SHEETS", "false").lower() == "true":
        required_vars += ["GOOGLE_SERVICE_ACCOUNT_JSON", "SPREADSHEET_ID"]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")