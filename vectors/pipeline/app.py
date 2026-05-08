<<<<<<< HEAD
=======
import os
import logging
>>>>>>> 185d04f (feat: implement pipeline/storage vector stubs, contracts, and dev agent team)
from flask import Flask
from routes import register_routes

logging.basicConfig(level=logging.INFO)


def create_app():
    app = Flask(__name__)
    app.config["NLP_PROVIDER"] = os.environ.get("NLP_PROVIDER", "claude")
    app.config["ANTHROPIC_API_KEY"] = os.environ.get("ANTHROPIC_API_KEY", "")
    app.config["MISTRAL_API_KEY"] = os.environ.get("MISTRAL_API_KEY", "")
    register_routes(app)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)), debug=False)
