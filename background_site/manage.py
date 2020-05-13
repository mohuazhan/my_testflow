# coding=utf-8

from master import create_app
from master.extensions import db
from db_backup import insert_task, insert_limit


app = create_app('production')
app_ctx = app.app_context()
with app_ctx:
    # 创建数据表
    db.create_all()
    # 项目启动时插入任务记录
    insert_task()
    # 项目启动时插入限制项及默认限制数
    insert_limit()

# 网站启动运行
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)