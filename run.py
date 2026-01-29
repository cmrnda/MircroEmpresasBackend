from dotenv import load_dotenv
load_dotenv()
from app import create_app
import os
app = create_app()
if __name__ == "__main__":
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", 5000))
    app.run(host=host, port=port, debug=True)