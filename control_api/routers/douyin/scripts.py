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
# 定义私信用户的公共步骤
def chat_step(device_id, chat_content, db, douyin_name, chat_user):
    dev = connect_device('Android:///%s'% device_id)
    # 点击发送消息
    touch((250, 1190), times=5)
    sleep(1)
    # 输入要发送的内容
    text(chat_content['text'], enter=False)  # 输入聊天内容后不要回车
    # 点击发送
    touch(Template(r"routers/douyin/res/img/send_chattext.png"))
    chat_log = log_chat(db, douyin_name, chat_user, chat_content['label'])
    # 账号信息表中当天私信人数加1
    if douyin_name != None:
        update_ca = update_chat_count(db, douyin_name)
    else:
        pass
    db.remove()
    keyevent("BACK")
    # 返回两次后再次输入其他账号搜索
    sleep(3)
    keyevent("BACK")
    sleep(3)
    keyevent("BACK")
    sleep(3)
    # 再次返回恢复搜索框
    keyevent("BACK")
    return

# 定义用账号密码(美国地区)登录抖音号的公共步骤
def login_step(device_id, account, password):
    dev = connect_device('Android:///%s'% device_id)
    poco = AndroidUiautomationPoco(dev, use_airtest_input=True, screenshot_each_action=False)
    # 如果当前地区不是美国，则循环执行地区选择
    while not exists(Template(r"routers/douyin/res/img/area_1.png")):
        # 点击 +86，选择手机号地区
        try:
            poco(text='+86').click()
        except:
            touch((118, 389))
        sleep(2)
        # 点击右侧首字母列表定位到T处
        touch((701, 909))
        # 如果出现美国则点击，否则上划到出现为止
        while not exists(Template(r"routers/douyin/res/img/america.png", threshold=0.9, rgb=True)):
            swipe((350,1100),(530,300))
            sleep(1)
        touch(Template(r"routers/douyin/res/img/america.png", threshold=0.9, rgb=True))
    sleep(2)
    # 点击 密码登录
    try:
        poco(text='密码登录').click()
    except:
        touch((111, 650))
    sleep(1)
    # 点击 请输入手机号
    try:
        poco(text='请输入手机号').click()
    except:
        touch((225, 333))
    sleep(1)
    # 输入手机号
    text(account, enter=False)
    sleep(2)
    # 点击 请输入密码
    try:
        poco(name='com.ss.android.ugc.aweme:id/dfk').click()
    except:
        touch((225, 333))
    sleep(1)
    # 输入密码
    text(password, enter=False)
    sleep(2)
    # 如果出现阅读并同意协议，则打勾后点击登录，否则直接点击登录
    if exists(Template(r"routers/douyin/res/img/read_and_agree.png", threshold=0.9, rgb=True)):
        touch(Template(r"routers/douyin/res/img/read_and_agree.png", threshold=0.9, rgb=True))
        # 点击 登录
        try:
            poco(text='登录').click()
        except:
            touch((360, 700))
    else:
        # 点击 登录
        try:
            poco(text='登录').click()
        except:
            touch((360, 628))
    sleep(8)
    # 如果出现跳过则点击
    if exists(Template(r"routers/douyin/res/img/skip.png", threshold=0.8, rgb=True)):
        touch(Template(r"routers/douyin/res/img/skip.png", threshold=0.8, rgb=True))
    else:
        pass
    # 如果出现 上滑查看更多视频 则上划
    if exists(Template(r"routers/douyin/res/img/swipe_up_readmore.png", threshold=0.7, rgb=True)):
        swipe((350,1100),(530,300))
    else:
        pass
    return


'''
以下部分为API所引用的函数
'''
# 检查是否已经安装抖音
def check_install_douyin(device_id):
    dev = connect_device('Android:///%s'% device_id)
    # 检查package是否在手机上，存在则返回True，否则报错，所有使用try...except处理
    try:
        res = dev.check_app('com.ss.android.ugc.aweme')
        return {"msg": "The device already installs!"}
    except:
        dev.install_app("routers/douyin/res/app/com.ss.android.ugc.aweme.apk", replace=True)
        # 任务结束将当前任务设为None
        task_none = reset_task(db, device_id)
        return {"msg": "Install successfully!"}

# 检查是否已经安装Yosemite
def check_install_yosemite(device_id):
    dev = connect_device('Android:///%s'% device_id)
    # 检查package是否在手机上，存在则返回True，否则报错，所有使用try...except处理
    try:
        res = dev.check_app('com.netease.nie.yosemite')
        return {"msg": "The device already installs!"}
    except:
        dev.install_app("routers/douyin/res/app/Yosemite.apk", replace=True)
        # 任务结束将当前任务设为None
        task_none = reset_task(db, device_id)
        return {"msg": "Install successfully!"}

# 登录/切换 抖音号
def login_douyin(device_id):
    # 优先获取没有自动化登录过的账号，其次获取当天上线次数最少的账号
    platform = '抖音'
    acc = get_douyin_acc_noname(db, device_id, platform)
    if acc == None:
        acc = get_douyin_acc_logless(db, device_id, platform)
        if acc == None:
            return None
        else:
            username = acc['username']
            account = acc['account']
            password = acc['password']
    else:
        username = acc['username']
        account = acc['account']
        password = acc['password']

    dev = connect_device('Android:///%s'% device_id)
    stop_app('com.ss.android.ugc.aweme')
    sleep(3)
    start_app('com.ss.android.ugc.aweme')
    sleep(3)
    poco = AndroidUiautomationPoco(dev, use_airtest_input=True, screenshot_each_action=False)
    # 如果出现通知则点击 取消
    if exists(Template(r"routers/douyin/res/img/cancel.png", threshold=0.8, rgb=True)):
        touch(Template(r"routers/douyin/res/img/cancel.png", threshold=0.8, rgb=True))
    else:
        pass
    # 点击 我
    try:
        poco(text='我').click()
    except:
        touch((650, 1208), duration=0.1, times=2)
    sleep(3)    
    # 如果出现编辑资料则执行退出账号，然后点击 我 执行登录账号（已有账号登录）
    if exists(Template(r"routers/douyin/res/img/edit_profile.png", threshold=0.7, rgb=True)):
        # 点击 更多 按钮
        try:
            poco(desc='更多').click()
        except:
            touch((650, 88))
        sleep(2)
        # 点击 设置
        try:
            poco(text='设置').click()
        except:
            touch((338, 909))
        sleep(2)
        # 如果出现退出登录则点击，否则上划到出现为止
        while not exists(Template(r"routers/douyin/res/img/log_out.png", threshold=0.7, rgb=True)):
            swipe((350,1100),(530,300))
            sleep(1)
        touch(Template(r"routers/douyin/res/img/log_out.png", threshold=0.7, rgb=True))
        sleep(2)
        # 点击 退出
        try:
            poco(text='退出').click()
        except:
            touch((555, 705))
        sleep(5)
        # 点击 我
        try:
            poco(text='我').click()
        except:
            touch((650, 1208), duration=0.1, times=2)
    else:
        pass
    # 如果出现一键登录则执行按账号密码登录（曾有账号登录但已下线）
    if exists(Template(r"routers/douyin/res/img/one_click_login.png", threshold=0.7, rgb=True)):
        # 点击 以其他帐号登录中 登录 两字 
        touch((420, 1170))
        sleep(3)
        login_step(device_id, account, password)
    # 如果出现登录后即可展示自己，则执行按账号密码登录（未曾有账号登录）
    elif exists(Template(r"routers/douyin/res/img/show_after_login.png", threshold=0.7, rgb=True)):
        login_step(device_id, account, password)
    # 如果用户名为空则获取用户名插入到账号设置表，否则跳过
    if username == None:
        # 点击 我
        try:
            poco(text='我').click()
        except:
            touch((650, 1208), duration=0.1, times=2)
        sleep(12)
        try:
            # 获取本账号抖音名
            freeze_poco = poco.freeze()  # 冻结poco，使操作更快
            douyin_name = freeze_poco(name="com.ss.android.ugc.aweme:id/d8b").get_text()
        except:
            douyin_name = None
        # 将抖音名插入账号设置表
        insert_username(db, douyin_name, account)
    else:
        pass
    db.remove()

# 切换任务
def change_task(device_id, task):
    dev = connect_device('Android:///%s'% device_id)
    stop_app('com.ss.android.ugc.aweme')
    sleep(3)
    start_app('com.ss.android.ugc.aweme')
    sleep(3)
    poco = AndroidUiautomationPoco(dev, use_airtest_input=True, screenshot_each_action=False)
    
    # 搜关键词功能是用模拟器实现，针对MUMU模拟器上的抖音版本做兼容
    if task == '搜关键词':
        douyin_name = '无（模拟器非登录下抓取）'
        # 获取关键词
        keyword = get_keyword(db)
        # 当仍有未搜关键词则继续搜索
        while keyword != None:
            insert_sql = insert_keyword(db, douyin_name, keyword)
            sleep(30)
            # 点击搜索
            try:
                poco(desc='搜索').click()
            except:
                touch((765, 75), times=1)
            # 输入关键词搜索
            text(keyword, search=True)
            sleep(3)
            # 点击 用户
            try:
                poco(text='用户').click()
            except:
                touch((368, 165), times=1)
            # 当没有更多时终止当前关键词，并开始新的关键词搜索，有些版本的抖音是'暂时没有更多了'
            while not poco(text="没有更多了").exists():
                swipe((530,1300),(530,300))  # 向上滑动到下一部分用户
                swipe((530,1300),(530,300))  # 连续滑动两次
                sleep(10)
            stop_app('com.ss.android.ugc.aweme')
            sleep(5)
            start_app('com.ss.android.ugc.aweme')
            # 获取新的未搜关键词
            keyword = get_keyword(db)
        db.remove()
        return
    else:
        pass
    
    while True:
        login_douyin(device_id)
        # 以下部分为养号和私信功能，针对OPPO A59s做兼容
        # 当识别到出现 检测到更新 时，点击 以后再说
        if exists(Template(r"routers/douyin/res/img/update_later.png")):
            touch(Template(r"routers/douyin/res/img/update_later.png"))
        else:
            pass
        # 点击 我
        try:
            poco(text='我').click()
        except:
            touch((650, 1208), duration=0.1, times=2)
        sleep(10)
        try:
            # 获取本账号抖音名
            freeze_poco = poco.freeze()  # 冻结poco，使操作更快
            douyin_name = freeze_poco(name="com.ss.android.ugc.aweme:id/d8b").get_text()
            # 将抖音名插入账号信息表
            insert_acc = insert_account(db, douyin_name, task)
        except:
            douyin_name = None
        # 在设备管理表中更新当前抖音号
        update_sql = update_dyname(db, device_id, douyin_name)
        # 点击首页
        try:
            poco(text='首页').click()
        except:
            touch((70, 1211), times=1)

        if task == '养号':
            swipe_times = 0
            # 观看40条视频后结束
            limit_times = get_limit_times(db, '每台设备单次养号观看视频数')
            while swipe_times < limit_times:
                # 当识别到出现 检测到更新 时，点击 以后再说
                if exists(Template(r"routers/douyin/res/img/update_later.png")):
                    touch(Template(r"routers/douyin/res/img/update_later.png"))
                # 当检测不到发布视频时，重启抖音，继续刷视频
                elif not exists(Template(r"routers/douyin/res/img/publish_video.png")):
                    # return None  # 之前使用这句话当出现异常情况时就会停止操作，方便终止任务
                    stop_app('com.ss.android.ugc.aweme')
                    sleep(3)
                    start_app('com.ss.android.ugc.aweme')
                    sleep(3)
                    poco = AndroidUiautomationPoco(dev, use_airtest_input=True, screenshot_each_action=False)
                watch_time = random.randint(30,50)
                time.sleep(watch_time)  # 30到50秒随机数停留
                # 收集视频信息
                try:
                    freeze_poco = poco.freeze()  # 冻结poco，使操作更快
                    father = freeze_poco("com.ss.android.ugc.aweme:id/bbt").offspring("com.ss.android.ugc.aweme:id/cxj").offspring("com.ss.android.ugc.aweme:id/b4i").offspring("com.ss.android.ugc.aweme:id/cv3")
                    author = '未知'
                    title = father.offspring("com.ss.android.ugc.aweme:id/a90").get_text()
                    point = father.offspring("com.ss.android.ugc.aweme:id/aly").get_text()
                    comment = father.offspring("com.ss.android.ugc.aweme:id/a7n").get_text()
                    share = father.offspring("com.ss.android.ugc.aweme:id/ekt").get_text()
                    insert_sql = collect_videos(db, douyin_name, author, title, point, comment, share)
                except:
                    pass
                # 账号信息表中当天观看视频数加1
                if douyin_name != None:
                    update_vd = update_video_count(db, douyin_name)
                else:
                    pass
                # 点击打开评论区
                try:
                    poco(descMatches='.*评论.*').click()
                except:
                    touch((656, 737), times=1)
                time.sleep(3)
                swipe((350,1000),(350,300))  # 向上滑动到下一部分评论
                # 按返回键关闭评论区
                keyevent("BACK")
                swipe((350,1100),(530,300))  # 向上滑动到下一条视频
                swipe_times += 1
        
        if task == '私信':
            # 点击搜索
            try:
                poco(desc='搜索').click()
            except:
                touch((666, 76))
            sleep(2)
            chat_num = 0
            limit_times = get_limit_times(db, '每台设备单次私信用户数')
            # 私信20人后结束
            while chat_num < limit_times:
                # 当识别到出现 检测到更新 时，点击 以后再说
                if exists(Template(r"routers/douyin/res/img/update_later.png")):
                    touch(Template(r"routers/douyin/res/img/update_later.png"))
                else:
                    pass
                # 获取还未私信的用户，和私信内容
                chat_user = get_chatuser(db)
                # 如果没有还没私信的用户则终止任务
                if chat_user == None:
                    break
                else:
                    pass
                chat_content = get_chattext(db)
                # 输入用户的id搜索
                text(chat_user, search=True)
                sleep(2)
                # 点击用户后，点击搜索出来的第一个用户
                try:
                    poco(text='用户').click()
                    poco("android:id/content").child("android.widget.FrameLayout").offspring("com.ss.android.ugc.aweme:id/ckn").child("android.widget.LinearLayout")[0].offspring("android.widget.ImageView").click()
                except:
                    touch((346, 175))
                    sleep(2)
                    touch((100, 300))
                # 如果搜索结果为空，则返回到搜索页
                if exists(Template(r"routers/douyin/res/img/search_none.png", rgb=True)):
                    sleep(3)
                    keyevent("BACK")
                # 如果是私密账号，则返回两次到搜索页
                elif exists(Template(r"routers/douyin/res/img/private_account.png", rgb=True)):
                    sleep(3)
                    keyevent("BACK")
                    sleep(3)
                    keyevent("BACK")
                # 如果是企业账号则直接私信
                elif exists(Template(r"routers/douyin/res/img/chat_business.png", rgb=True)):
                    touch(Template(r"routers/douyin/res/img/chat_business.png"))
                    sleep(3)
                    chat_step(device_id, chat_content, db, douyin_name, chat_user)
                    chat_num += 1
                # 如果已经关注则直接点击私信
                elif exists(Template(r"routers/douyin/res/img/chat_user.png")):  # rgb=True:强制指定使用彩色图像进行识别
                    # 点击私信
                    touch(Template(r"routers/douyin/res/img/chat_user.png"))
                    sleep(3)
                    chat_step(device_id, chat_content, db, douyin_name, chat_user)
                    chat_num += 1
                # 如果还没关注则直接关注后私信
                elif exists(Template(r"routers/douyin/res/img/follow.png", rgb=True)):
                    # 点击关注后私信
                    touch((429, 305))
                    sleep(2)
                    touch((527, 311))
                    sleep(3)
                    chat_step(device_id, chat_content, db, douyin_name, chat_user)
                    chat_num += 1
                # 如果出现特殊情况，则重启抖音，继续操作
                else:
                    # return None  # 没有识别出以上选择则终止任务
                    stop_app('com.ss.android.ugc.aweme')
                    sleep(3)
                    start_app('com.ss.android.ugc.aweme')
                    sleep(3)
                    poco = AndroidUiautomationPoco(dev, use_airtest_input=True, screenshot_each_action=False)
                    if exists(Template(r"routers/douyin/res/img/update_later.png")):
                        touch(Template(r"routers/douyin/res/img/update_later.png"))
                    else:
                        pass
                    try:
                        poco(desc='搜索').click()
                    except:
                        touch((666, 76))
                    sleep(2)

    # 任务结束将当前任务设为None
    task_none = reset_task(db, device_id)
    stop_app('com.ss.android.ugc.aweme')
    db.remove()
    return

# 终止任务
def stop_douyin(device_id):
    dev = connect_device('Android:///%s'% device_id)
    # 此时如果设备正执行任务，终止任务并不会让点击滑屏等操作停止
    # 所以要在执行任务的代码加入识别不到就return
    # 如果不加return，只能等该设备的当前任务执行完，或者终止代码运行或断开USB连接
    stop_app('com.ss.android.ugc.aweme')
    # 打开天气，随便另一个进程乱点直至停止
    start_app('com.coloros.weather')
    db.remove()
    return

# 根据文本批量导入账号
def import_douyin_acc(id):
    # 根据id获取账号批量导入表的文本
    all_acc = get_douyin_acc_text(db, id)
    acc_list = [
        each_acc for each_acc in all_acc.split(' ') \
        if 'http' in each_acc and \
        each_acc.count('http') == 1
    ]
    # 开始将切分的账号导入账号设置表
    platform = '抖音'
    start_import = insert_acc(db, acc_list, platform)
    db.remove()
    return