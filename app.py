"""
app.py — Flask application factory và điểm khởi động.
"""
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from config import Config
from models import db, TaiKhoan
from database import init_db

# ── Blueprints ─────────────────────────────────────────────
from routes.auth       import auth_bp
from routes.dashboard  import dashboard_bp
from routes.members    import members_bp
from routes.packages   import packages_bp
from routes.classes    import classes_bp
from routes.trainers   import trainers_bp
from routes.staff      import staff_bp
from routes.accounts   import accounts_bp
from routes.checkin    import checkin_bp
from routes.rooms      import rooms_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ── Extensions ────────────────────────────────────────
    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Vui lòng đăng nhập để tiếp tục.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return TaiKhoan.query.get(int(user_id))

    # ── Blueprints ─────────────────────────────────────────
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(members_bp,  url_prefix='/members')
    app.register_blueprint(packages_bp, url_prefix='/packages')
    app.register_blueprint(classes_bp,  url_prefix='/classes')
    app.register_blueprint(trainers_bp, url_prefix='/trainers')
    app.register_blueprint(staff_bp,    url_prefix='/staff')
    app.register_blueprint(accounts_bp, url_prefix='/accounts')
    app.register_blueprint(checkin_bp,  url_prefix='/checkin')
    app.register_blueprint(rooms_bp,    url_prefix='/rooms')

    # ── Root redirect ──────────────────────────────────────
    @app.route('/')
    def index():
        return redirect(url_for('dashboard.index'))

    # ── Jinja2 filters ─────────────────────────────────────
    @app.template_filter('vnd')
    def vnd_filter(value):
        """Format số thành dạng tiền VND."""
        try:
            return '{:,.0f}đ'.format(float(value))
        except (ValueError, TypeError):
            return '0đ'

    @app.template_filter('dateformat')
    def date_format(value, fmt='%d/%m/%Y'):
        if value is None:
            return '—'
        try:
            return value.strftime(fmt)
        except Exception:
            return str(value)

    @app.template_filter('datetimeformat')
    def datetime_format(value, fmt='%d/%m/%Y %H:%M'):
        if value is None:
            return '—'
        try:
            return value.strftime(fmt)
        except Exception:
            return str(value)

    return app


app = create_app()

if __name__ == '__main__':
    init_db(app)
    app.run(debug=True, host='0.0.0.0', port=5000)
