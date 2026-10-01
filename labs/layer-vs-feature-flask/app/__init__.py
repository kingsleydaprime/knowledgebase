from flask import Flask

from .extensions import db


def create_app(test_config=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///shop.db"
    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    # The composition root: the only place that knows which features exist.
    from .orders import bp as orders_bp
    from .users import bp as users_bp

    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(orders_bp, url_prefix="/api/orders")

    with app.app_context():
        db.create_all()
    return app
