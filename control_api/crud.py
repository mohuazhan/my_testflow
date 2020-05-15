# coding=utf-8

from sqlalchemy.orm import Session
import random
import datetime

from models import DeviceInfo, AccountInfo, \
                    KeywordInfo, ChatInfo, \
                    VideoInfo, WbAccountImport, \
                    DyAccountImport, AccountSetup, \
                    LimitSetup, KeywordSetup, \
                    ChatSetup

# 获取当天零点的时间
def today_min():
    today = datetime.datetime.today()
    return datetime.datetime(today.year, today.month, today.day, 0, 0, 0)

# 重置所有设备为断开
def update_dev_status(db: Session):
    # 先让所有设备的状态为已断开
    dev_all = db.query(DeviceInfo).all()
    if dev_all == None:
        pass
    else:
        for dev_each in dev_all:
            dev_each.status = '已断开'
            db.commit()

# 更新设备列表
def update_device(db: Session, device_id: str):
    dev = db.query(DeviceInfo).filter_by(device_id=device_id).first()
    # 如果设备串号不存在则插入，否则跳过
    if dev == None:
        # 创建一个新用户对象
        dev = DeviceInfo()
        dev.device_id = device_id
        dev.status = '已连接'
        db.add(dev)
        db.commit()
        # 插入成功后返回串号
        return {"msg": "%s add successfully!" % dev.device_id}
    else:
        # 如果设备已存在则将状态更新为已连接
        dev.status = '已连接'
        db.commit()
        # 告知设备已存在
        return {"msg": "The device already exists!"}

# 先在设备管理表中更新当前抖音号
def update_dyname(db: Session, device_id, douyin_name):
    dev = db.query(DeviceInfo).filter_by(device_id=device_id).first()
    dev.douyin_name = douyin_name
    db.commit()
    db.close()
    return True

# 收集观看过的视频信息
def collect_videos(db: Session, douyin_name, author, title, point, comment, share):
    video = VideoInfo()
    if '赞' in point:
        point = 0
    elif 'w' in point:
        point = int(float(point.replace('w',''))*10000)
    else:
        point = int(point)
    if '评论' in comment:
        comment = 0
    elif 'w' in comment:
        comment = int(float(comment.replace('w',''))*10000)
    else:
        comment = int(comment)
    if '分享' in share:
        share = 0
    elif 'w' in share:
        share = int(float(share.replace('w',''))*10000)
    else:
        share = int(share)
    video.douyin_name = douyin_name
    video.video_douyin_name = author
    video.video_title = title
    video.point_num = point
    video.comment_num = comment
    video.share_num = share
    video.watch_time = datetime.datetime.now()
    db.add(video)
    db.commit()
    db.close()
    return True

# 获取关键词
def get_keyword(db: Session):
    # 查找状态为空的关键词
    word = db.query(KeywordSetup).filter_by(status=None).first()
    if word == None:
        return None
    else:
        # 如果有未搜的关键词，将状态设为已捜，然后返回该关键词
        word.status = '已捜'
        keyword = word.keyword
        db.commit()
        db.close()
        return keyword

# 将搜索的关键词插入关键词信息表
def insert_keyword(db: Session, douyin_name, keyword):
    word = KeywordInfo()
    word.keyword = keyword
    word.douyin_name = douyin_name
    word.status = '已捜'
    word.search_time = datetime.datetime.now()
    db.add(word)
    db.commit()
    db.close()
    return True

# 获取还未私信的用户
def get_chatuser(db: Session):
    user = db.query(ChatInfo).filter_by(status=None).first()
    if user == None:
        return None
    else:
        # 如果有未私信的用户，则返回该用户的抖音id
        chat_user = user.chat_douyin_id
        user.status = '已私信'
        db.commit()
        db.close()
        return chat_user
    
# 获取已启用的私信内容
def get_chattext(db: Session):
    content = db.query(ChatSetup).filter_by(status='启用').all()
    # 如果还没设置可启用的私信内容，则默认私信内容为'你好'
    if content == None:
        return str('你好')
    else:
        # 从启用的私信内容中随机选取一个
        chat_one = random.choice(content)
        chat_text = chat_one.chat_content
        chat_label = chat_one.chat_label
        return {"text": chat_text, "label": chat_label}

# 更新私信记录
def log_chat(db: Session, douyin_name, chat_user, chat_label):
    user = db.query(ChatInfo).filter_by(chat_douyin_id=chat_user).first()
    if user == None:
        return None
    else:
        user.douyin_name = douyin_name
        user.chat_label = chat_label
        user.chat_time = datetime.datetime.now()
        db.commit()
        db.close()
        return True

# 任务结束设置当前任务为None
def reset_task(db: Session, device_id):
    dev = db.query(DeviceInfo).filter_by(device_id=device_id).first()
    dev.task_now = None
    db.commit()
    db.close()
    return True

# 将抖音名插入账号信息表
def insert_account(db: Session, douyin_name, task):
    acc = db.query(AccountInfo).filter_by(douyin_name=douyin_name).first()
    if acc == None:
        acc = AccountInfo()
        acc.douyin_name = douyin_name
        acc.task_now = task
        acc.online_times_td = 1
        acc.watch_times_td = 0
        acc.point_times_td = 0
        acc.comment_times_td = 0
        acc.chat_times_td = 0
        acc.login_time = datetime.datetime.now()
        db.add(acc)
        db.commit()
        db.close()
        return True
    else:
        acc.task_now = task
        # 当天初次登录时设上线次数为1，不是初次登录则次数加1
        if acc.login_time < today_min():
            acc.online_times_td = 1
            acc.watch_times_td = 0
            acc.point_times_td = 0
            acc.comment_times_td = 0
            acc.chat_times_td = 0
        else:
            acc.online_times_td += 1
        acc.login_time = datetime.datetime.now()
        db.commit()
        db.close()
        return True

# 账号信息表中当天观看视频数加1
def update_video_count(db: Session, douyin_name):
    acc = db.query(AccountInfo).filter_by(douyin_name=douyin_name).first()
    acc.watch_times_td += 1
    db.commit()
    db.close()
    return True

# 账号信息表中当天私信人数加1
def update_chat_count(db: Session, douyin_name):
    acc = db.query(AccountInfo).filter_by(douyin_name=douyin_name).first()
    acc.chat_times_td += 1
    db.commit()
    db.close()
    return True

# 获取批量导入的微博号文本
def get_weibo_acc_text(db: Session, id):
    acc = db.query(WbAccountImport).filter_by(id=id).first()
    all_acc = acc.account_text
    acc.status = '已导入'
    db.commit()
    db.close()
    return all_acc

# 获取批量导入的抖音号文本
def get_douyin_acc_text(db: Session, id):
    acc = db.query(DyAccountImport).filter_by(id=id).first()
    all_acc = acc.account_text
    acc.status = '已导入'
    db.commit()
    db.close()
    return all_acc

# 将切分的账号导入账号设置表
def insert_acc(db: Session, acc_list, platform):
    for each_acc in acc_list:
        acc = AccountSetup()
        if platform == '微博':
            # each_acc示例：'18307418590----uvcjji859'
            each_acc_list = each_acc.split('----')
            acc.account = each_acc_list[0]
            acc.password = each_acc_list[-1]
        elif platform == '抖音':
            # each_acc示例：'2894742776http://101.37.119.224/did/api/sms/getbytoken?token=beacd810fc6de99f4547949c44f8f9ae'
            each_acc_list = each_acc.split('http')
            acc.account = each_acc_list[0]
            acc.password = 'http' + each_acc_list[-1]
        acc.platform = platform
        acc.status = '启用'
        db.add(acc)
        db.commit()
        db.close()
    return True

# 获取未登录过的微博账号
def get_weibo_acc_withoutlog(db: Session, device_id, platform):
    acc = db.query(AccountSetup).filter_by(device_id=None, platform=platform, status='启用').first()
    if acc == None:
        return None
    else:
        username = acc.account
        password = acc.password
        acc.device_id = device_id
        db.commit()
        db.close()
        return {"username": username, "password": password}

# 获取限制项的限制数
def get_limit_times(db: Session, option):
    limit = db.query(LimitSetup).filter_by(limit_option=option).first()
    limit_times = limit.limit_times
    return limit_times

# 获取已填写设备串号和新密码但还没自动化登录过(用户名为None)的抖音账号
def get_douyin_acc_noname(db: Session, device_id, platform):
    acc = db.query(AccountSetup).filter_by(username=None, device_id=device_id, platform=platform, status='启用').first()
    if acc == None:
        return None
    else:
        username = acc.username
        account = acc.account
        password = acc.new_password
        return {"username": username, "account": account, "password": password}

# 根据抖音号到账号信息表中获取当天上线次数
def get_online_times_today(db: Session, douyin_name):
    acc = db.query(AccountInfo).filter_by(douyin_name=douyin_name).first()
    if acc == None:
        return None
    else:
        online_times_td = acc.online_times_td
        return online_times_td

# 获取当天上线次数最少的抖音账号
def get_douyin_acc_logless(db: Session, device_id, platform):
    all_acc = db.query(AccountSetup).filter_by(device_id=device_id, platform=platform, status='启用').all()
    if all_acc == None:
        return None
    else:
        less_online_times_td = None
        username = None
        account = None
        password = None
        for each_acc in all_acc:
            # 如果还没自动化登录过(用户名为None)则跳过
            if each_acc.username == None:
                pass
            else:
                douyin_name = each_acc.username
                # 根据抖音号到账号信息表中查看当天上线次数
                online_times_td = get_online_times_today(db, douyin_name)
                if less_online_times_td == None:
                    less_online_times_td = online_times_td
                    username = each_acc.username
                    account = each_acc.account
                    password = each_acc.new_password
                elif online_times_td < less_online_times_td:
                    less_online_times_td = online_times_td
                    username = each_acc.username
                    account = each_acc.account
                    password = each_acc.new_password
                else:
                    pass
        return {"username": username, "account": account, "password": password}

# 将抖音名插入账号设置表
def insert_username(db: Session, douyin_name, account):
    acc = db.query(AccountSetup).filter_by(account=account).first()
    acc.username = douyin_name
    db.commit()
    db.close()

# 获取当前任务进程pid
def get_task_pid(db: Session, device_id):
    dev = db.query(DeviceInfo).filter_by(device_id=device_id).first()
    if dev.task_pid == None:
        return None
    else:
        task_pid = dev.task_pid
        return task_pid


# 重置当前任务进程pid
def reset_task_pid(db: Session, device_id, task_pid):
    dev = db.query(DeviceInfo).filter_by(device_id=device_id).first()
    dev.task_pid = task_pid
    db.commit()
    db.close()
    return True


# 以下代码为测试示例
# from database import SessionLocal
# db = SessionLocal()
# get_limit_times(db, '每台设备单次私信用户数')
# get_douyin_acc_text(db, 1)
# get_douyin_acc_logless(db, 'MJEQOR5H75BY45SS', '抖音')