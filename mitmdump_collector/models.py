# coding=utf-8

from sqlalchemy import Column, Integer, String, DateTime

from database import Base

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

