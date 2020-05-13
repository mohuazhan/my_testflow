# coding=utf-8

from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_babelex import Babel

db = SQLAlchemy()
admin = Admin(name='抖音自动化管理系统', template_mode='bootstrap3')
babel = Babel()