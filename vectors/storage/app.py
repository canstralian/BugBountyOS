from flask import Flask
from flask_sqlalchemy import SQLAlchemy

logging.basicConfig(level=logging.INFO)

db = SQLAlchemy()


def create_app(config: dict | None = None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///storage.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    if config:
        app.config.update(config)
    db.init_app(app)

    with app.app_context():
        import models  # noqa: F401 — registers models with SQLAlchemy
        db.create_all()

    from routes import register_routes
    register_routes(app)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5002)), debug=False)
