from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from utils import my_path, my_config

db = SQLAlchemy()

migrate = Migrate(db=db)


def init_app(app):
    """
    初始化 Flask 应用
    """
    # 设置数据库 URI，这里使用 SQLite 作为示例
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{my_path(my_config("database", "dir"))}'

    # 配置 SQLAlchemy，禁用警告
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 初始化 SQLAlchemy 实例
    db.init_app(app)


def create_all():
    return db.create_all()
