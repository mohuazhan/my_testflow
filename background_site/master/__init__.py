# coding=utf-8

from flask import Flask, session, request, redirect, url_for
from master.extensions import db, admin, babel
from master.settings import config
from master.blueprints.admin import admin_bp

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'production')

    # Flask实例化，生成对象app
    app = Flask('master')
    # 设置app的配置信息
    app.config.from_object(config[config_name])

    register_extensions(app)
    register_blueprints(app)

    @app.before_request
    def check():
        if (not session.get('user') and not request.path.startswith('/static') \
            and request.path != '/login'):
            return redirect(url_for('admin_bk.login'))

    return app


def register_extensions(app):
    # 将Flask与SQLAlchemy绑定
    db.init_app(app)
    # 定义admin后台
    admin.init_app(app)
    # 本地化，将Admin改为中文显示
    babel.init_app(app)


def register_blueprints(app):
    app.register_blueprint(admin_bp)


