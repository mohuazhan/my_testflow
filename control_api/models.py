# coding=utf-8

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.mysql import LONGTEXT

from database import Base

# 定义设备信息表
class DeviceInfo(Base):
    # db.Column是定义字段、db.INT是字段的数据类型
    __tablename__ = 'device_info'  # 表名称

    id = Column(Integer, primary_key=True)
    device_id = Column(String)  # 手机设备串号
    douyin_name = Column(String)  # 当前登录的抖音号
    task_now = Column(String)  # 当前任务
    start_times_td = Column(Integer)  # 今天启动次数
    start_times_all = Column(Integer)  # 启动总次数
    status = Column(String)  # 状态
    start_time = Column(DateTime)  # 最近一次启动时间

# 定义账号信息表
class AccountInfo(Base):
    __tablename__ = 'account_info'

    id = Column(Integer, primary_key=True)
    douyin_name = Column(String)  # 抖音号
    task_now = Column(String)  # 当前任务
    online_times_td = Column(Integer)  # 今天上线次数
    watch_times_td = Column(Integer)  # 今天观看视频数
    point_times_td = Column(Integer)  # 今天点赞数
    comment_times_td = Column(Integer)  # 今天评论数
    chat_times_td = Column(Integer)  # 今天私信人数
    login_time = Column(DateTime)  # 最近一次登录时间

# 定义关键词信息表
class KeywordInfo(Base):
    __tablename__ = 'keyword_info'

    id = Column(Integer, primary_key=True)
    keyword = Column(String)  # 关键词
    douyin_name = Column(String)  # 搜索该词的抖音号
    status = Column(String)  # 状态：已捜/未搜
    search_time = Column(DateTime)  # 搜索时间

# 定义私信信息表
class ChatInfo(Base):
    __tablename__ = 'chat_info'

    id = Column(Integer, primary_key=True)
    chat_douyin_id = Column(String)  # 私信的抖音id
    chat_douyin_name = Column(String)  # 私信的抖音号
    douyin_name = Column(String)  # 私信使用的抖音号
    fans_num = Column(Integer)  # 粉丝数
    keyword = Column(String)  # 来源关键词
    status = Column(String)  # 状态：已私信/未私信(为空)
    chat_label = Column(String)  # 私信标签
    chat_time = Column(DateTime)  # 私信时间

# 定义视频信息表
class VideoInfo(Base):
    __tablename__ = 'video_info'

    id = Column(Integer, primary_key=True)
    video_douyin_name = Column(String)  # 视频作者抖音号
    video_title = Column(String)  # 视频标题
    douyin_name = Column(String)  # 观看该视频的抖音号
    point_num = Column(Integer)  # 当前点赞数
    comment_num = Column(Integer)  # 当前评论数
    share_num = Column(Integer)  # 当前评论数
    watch_time = Column(DateTime)  # 观看时间

# 定义微博账号导入表
class WbAccountImport(Base):
    __tablename__ = 'wb_account_import'

    id = Column(Integer, primary_key=True)
    account_text = Column(LONGTEXT)  # 批量帐号的文本
    status = Column(String)  # 状态：已导入/未导入(为空)

# 定义抖音账号导入表
class DyAccountImport(Base):
    __tablename__ = 'dy_account_import'

    id = Column(Integer, primary_key=True)
    account_text = Column(LONGTEXT)  # 批量帐号的文本
    status = Column(String)  # 状态：已导入/未导入(为空)

# 定义账号设置表
class AccountSetup(Base):
    __tablename__ = 'account_setup'

    id = Column(Integer, primary_key=True)
    username = Column(String)  # 该账户的用户名（如抖音名,微博名）
    device_id = Column(String)  # 所登录的手机设备串号
    account = Column(String)  # 账号
    password = Column(String)  # 密码（或验证码url）
    new_password = Column(String)  # 重新设置的密码
    platform = Column(String)  # 第三方平台
    status = Column(String)  # 状态：启用/禁用

# 定义限制项设置表
class LimitSetup(Base):
    __tablename__ = 'limit_setup'

    id = Column(Integer, primary_key=True)
    limit_option = Column(String)  # 限制项
    limit_times = Column(Integer)  # 限制数

# 定义关键词设置表
class KeywordSetup(Base):
    __tablename__ = 'keyword_setup'

    id = Column(Integer, primary_key=True)
    keyword = Column(String)  # 关键词
    status = Column(String)  # 状态：已捜/未搜(为空)

# 定义私信设置表
class ChatSetup(Base):
    __tablename__ = 'chat_setup'

    id = Column(Integer, primary_key=True)
    chat_label = Column(String)  # 私信标签
    chat_content = Column(String)  # 私信内容
    status = Column(String)  # 状态：启用/禁用
