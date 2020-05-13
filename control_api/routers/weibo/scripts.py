# coding=utf-8

from crud import *
from database import SessionLocal

from airtest.core.api import *
from airtest.core.android.android import Android
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
import time
import random
from sqlalchemy.orm import scoped_session

# 加上log级别的设定，取消脚本执行过程中刷新大量的log信息
import logging
logger = logging.getLogger("airtest")
logger.setLevel(logging.ERROR)

# 调用了scoped_session_maker.remove()后
# 再用scoped_session_maker()创建的session对象和之前创建的就是不同的对象了
db = scoped_session(SessionLocal)

'''
以下部分为本文件内部引用函数
'''
# 定义登录账号的公共步骤
def login_step(device_id, username, password):
    dev = connect_device('Android:///%s'% device_id)
    # 点击用账号密码登录
    try:
        poco(text='用帐号密码登录').click()
    except:
        touch((360, 808), times=1)
    sleep(2)
    # 输入账号密码
    try:
        poco(name='com.sina.weibo:id/et_pws_username').set_text(username)
        poco(name='com.sina.weibo:id/et_pwd').set_text(password)
    except:
        touch((170, 443))
        sleep(1)
        text(username, enter=False)
        sleep(2)
        touch((170, 534))
        sleep(1)
        text(password, enter=False)
    sleep(3)
    # 点击登录
    try:
        poco(text='登录').click()
    except:
        touch((355, 697))
    sleep(10)


'''
以下部分为API所引用的函数
'''
# 检查是否已经安装微博
def check_install_weibo(device_id):
    dev = connect_device('Android:///%s'% device_id)
    # 检查package是否在手机上，存在则返回True，否则报错，所有使用try...except处理
    try:
        res = dev.check_app('com.sina.weibo')
        return {"msg": "The device already installs!"}
    except:
        dev.install_app("routers/weibo/res/app/com.sina.weibo.apk", replace=True)
        # 任务结束将当前任务设为None
        task_none = reset_task(db, device_id)
        return {"msg": "Install successfully!"}

# 根据文本批量导入账号
def import_weibo_acc(id):
    # 根据id获取账号批量导入表的文本
    all_acc = get_weibo_acc_text(db, id)
    # 列表推导式，按空格切分原始文本，且每个账号密码只包含一个'----'
    acc_list = [
        each_acc for each_acc in all_acc.split(' ') \
        if '----' in each_acc and \
        each_acc.count('----') == 1
    ]
    # 开始将切分的账号导入账号设置表
    platform = '微博'
    start_import = insert_acc(db, acc_list, platform)
    db.remove()
    return

# 微博账号批量登录
def login_weibo(device_id):
    dev = connect_device('Android:///%s'% device_id)
    stop_app('com.sina.weibo')
    sleep(3)
    start_app('com.sina.weibo')
    sleep(3)
    poco = AndroidUiautomationPoco(dev, use_airtest_input=True, screenshot_each_action=False)
    sleep(5)
    num = 0
    limit_times = get_limit_times(db, '每台设备登录微博账号数')
    while num < limit_times:
        # 获取未登录过的微博账号
        platform = '微博'
        weibo_acc = get_weibo_acc_withoutlog(db, device_id, platform)
        # 如果没有还未登录过的账号则终止
        if weibo_acc == None:
            break
        else:
            pass
        username = weibo_acc['username']
        password = weibo_acc['password']
        # 如果已登录了账号
        if exists(Template(r"routers/weibo/res/img/me.png", rgb=True)):
            # 点击我
            touch((645, 1215))
            sleep(10)  # 这里等待10秒是为了等一些弹窗消失
            # 点击设置
            touch((662, 80))
            sleep(3)
            # 点击账号管理
            touch((100, 193))
            sleep(3)
            # 如果存在添加账号的按钮则点击，否则上划到出现为止
            while not exists(Template(r"routers/weibo/res/img/add_login.png")):
                swipe((350,1100),(530,300))
                sleep(1)
            touch(Template(r"routers/weibo/res/img/add_login.png"))
            # 执行登录步骤
            login_step(device_id, username, password)
            num += 1
        # 如果还没登录过账号
        elif exists(Template(r"routers/weibo/res/img/login_weibo.png")):
            login_step(device_id, username, password)
            num += 1
        # 否则重启微博继续登录
        else:
            stop_app('com.sina.weibo')
            sleep(3)
            start_app('com.sina.weibo')
            sleep(3)

    # 任务结束将当前任务设为None
    task_none = reset_task(db, device_id)
    stop_app('com.sina.weibo')
    db.remove()
    return