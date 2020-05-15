# coding=utf-8

from master.extensions import db

from sqlalchemy.dialects.mysql import LONGTEXT


# 定义任务管理表
class TaskInfo(db.Model):
    # db.Column是定义字段、db.INT是字段的数据类型
    __tablename__ = 'task_info'  # 表名称

    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(50))  # 任务名
    start_time = db.Column(db.DateTime)  # 最近一次启动时间


# 定义设备管理表
class DeviceInfo(db.Model):
    # db.Column是定义字段、db.INT是字段的数据类型
    __tablename__ = 'device_info'  # 表名称

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(50))  # 手机设备串号
    douyin_name = db.Column(db.String(50))  # 当前登录的抖音号
    task_now = db.Column(db.String(50))  # 当前任务
    task_pid = db.Column(db.Integer)  # 当前任务进程pid
    start_times_td = db.Column(db.Integer)  # 今天启动次数
    start_times_all = db.Column(db.Integer)  # 启动总次数
    status = db.Column(db.String(50))  # 状态：已连接/已断开
    start_time = db.Column(db.DateTime)  # 最近一次启动时间


# 定义账号信息表
class AccountInfo(db.Model):
    __tablename__ = 'account_info'

    id = db.Column(db.Integer, primary_key=True)
    douyin_name = db.Column(db.String(50))  # 抖音号
    task_now = db.Column(db.String(50))  # 当前任务
    online_times_td = db.Column(db.Integer)  # 今天上线次数
    watch_times_td = db.Column(db.Integer)  # 今天观看视频数
    point_times_td = db.Column(db.Integer)  # 今天点赞数
    comment_times_td = db.Column(db.Integer)  # 今天评论数
    chat_times_td = db.Column(db.Integer)  # 今天私信人数
    login_time = db.Column(db.DateTime)  # 最近一次登录时间


# 定义关键词信息表
class KeywordInfo(db.Model):
    __tablename__ = 'keyword_info'

    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(50))  # 关键词
    douyin_name = db.Column(db.String(50))  # 搜索该词的抖音号
    status = db.Column(db.String(50))  # 状态：已捜/未搜
    search_time = db.Column(db.DateTime)  # 搜索时间


# 定义私信信息表
class ChatInfo(db.Model):
    __tablename__ = 'chat_info'

    id = db.Column(db.Integer, primary_key=True)
    chat_douyin_id = db.Column(db.String(50))  # 私信的抖音id
    chat_douyin_name = db.Column(db.String(50))  # 私信的抖音号
    douyin_name = db.Column(db.String(50))  # 私信使用的抖音号
    fans_num = db.Column(db.Integer)  # 粉丝数
    keyword = db.Column(db.String(50))  # 来源关键词
    status = db.Column(db.String(50))  # 状态：已私信/未私信(为空)
    chat_label = db.Column(db.String(500))  # 私信标签
    chat_time = db.Column(db.DateTime)  # 私信时间


# 定义视频信息表
class VideoInfo(db.Model):
    __tablename__ = 'video_info'

    id = db.Column(db.Integer, primary_key=True)
    video_douyin_name = db.Column(db.String(50))  # 视频作者抖音号
    video_title = db.Column(db.String(500))  # 视频标题
    douyin_name = db.Column(db.String(50))  # 观看该视频的抖音号
    point_num = db.Column(db.Integer)  # 当前点赞数
    comment_num = db.Column(db.Integer)  # 当前评论数
    share_num = db.Column(db.Integer)  # 当前评论数
    watch_time = db.Column(db.DateTime)  # 观看时间


# 定义微博账号导入表
class WbAccountImport(db.Model):
    __tablename__ = 'wb_account_import'

    id = db.Column(db.Integer, primary_key=True)
    account_text = db.Column(LONGTEXT)  # 批量帐号的文本
    status = db.Column(db.String(50))  # 状态：已导入/未导入(为空)


# 定义抖音账号导入表
class DyAccountImport(db.Model):
    __tablename__ = 'dy_account_import'

    id = db.Column(db.Integer, primary_key=True)
    account_text = db.Column(LONGTEXT)  # 批量帐号的文本
    status = db.Column(db.String(50))  # 状态：已导入/未导入(为空)


# 定义账号设置表
class AccountSetup(db.Model):
    __tablename__ = 'account_setup'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))  # 该账户的用户名（如抖音名,微博名）
    device_id = db.Column(db.String(50))  # 所登录的手机设备串号
    account = db.Column(db.String(50))  # 账号
    password = db.Column(db.String(200))  # 密码（或验证码url）
    new_password = db.Column(db.String(50))  # 重新设置的密码
    platform = db.Column(db.String(50))  # 第三方平台
    status = db.Column(db.String(50))  # 状态：启用/禁用


# 定义限制项设置表
class LimitSetup(db.Model):
    __tablename__ = 'limit_setup'

    id = db.Column(db.Integer, primary_key=True)
    limit_option = db.Column(db.String(50))  # 限制项
    limit_times = db.Column(db.Integer)  # 限制数


# 定义关键词设置表
class KeywordSetup(db.Model):
    __tablename__ = 'keyword_setup'

    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(50))  # 关键词
    status = db.Column(db.String(50))  # 状态：已捜/未搜(为空)


# 定义私信设置表
class ChatSetup(db.Model):
    __tablename__ = 'chat_setup'

    id = db.Column(db.Integer, primary_key=True)
    chat_label = db.Column(db.String(50))  # 私信标签
    chat_content = db.Column(db.String(500))  # 私信内容
    status = db.Column(db.String(50))  # 状态：启用/禁用

