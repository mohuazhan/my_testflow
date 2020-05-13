# coding=utf-8

from master.models import TaskInfo, LimitSetup
from master.extensions import db

# 项目启动时插入任务
def insert_task():
    task_list = [
        '更新设备列表',
        '模拟器自动搜关键词',
        '所有设备自动养号',
        '所有设备自动私信'
        ]
    for task in task_list:
        res = TaskInfo.query.filter_by(task=task).first()
        # 项目启动前查询任务管理表是否有任务记录，没有则插入
        if res == None:
            # 创建一个新用户对象
            res = TaskInfo()
            res.task = task
            db.session.add(res)
            db.session.commit()
        else:
            pass
    db.session.close()

# 项目启动时插入限制项及默认限制数
def insert_limit():
    limit_list = [
        {'每台设备登录微博账号数': 30},
        {'每台设备单次养号观看视频数': 30},
        {'每台设备单次私信用户数': 20}
        ]
    for limit in limit_list:
        limit_option = list(limit.keys())[0]
        limit_times = list(limit.values())[0]
        res = LimitSetup.query.filter_by(limit_option=limit_option).first()
        # 项目启动前查询任务管理表是否有任务记录，没有则插入
        if res == None:
            # 创建一个新用户对象
            res = LimitSetup()
            res.limit_option = limit_option
            res.limit_times = limit_times
            db.session.add(res)
            db.session.commit()
        else:
            pass
    db.session.close()