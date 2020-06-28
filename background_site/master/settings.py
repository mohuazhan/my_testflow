# coding=utf-8


class BaseConfig(object):
    # 设置中文
    BABEL_DEFAULT_LOCALE = 'zh_CN'
    # 设置密钥值，用于Session、Cookies以及扩展模块
    SECRET_KEY = 'xiaomo20200315'
    # 解决Json乱码
    JSON_AS_ASCII = False
    # 设置可选启动样本主题
    FLASK_ADMIN_SWATCH = 'default'


class ProductionConfig(BaseConfig):
    # 设置SQLAlchemy连接数据库
    SQLALCHEMY_DATABASE_URI =\
    'mysql+mysqlconnector://xiaomo:password@localhost:3306/auto_dy?charset=utf8mb4'
    # 在每次请求结束后自动提交数据库改变
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    # 如果设置成True,将会追踪对象的修改并且发送信号,这需要额外的内存,如果不必要可以禁用它。
    SQLALCHEMY_TRACK_MODIFICATIONS = False


config = {
    'production': ProductionConfig
}
