# coding=utf-8

from models import ChatInfo
from database import SessionLocal

from sqlalchemy.orm import Session
from sqlalchemy.orm import scoped_session
from mitmproxy import ctx
import json

# 调用了scoped_session_maker.remove()后
# 再用scoped_session_maker()创建的session对象和之前创建的就是不同的对象了
db = scoped_session(SessionLocal)

info = ctx.log.info

kw_search_user_url = "https://search-lf.amemv.com/aweme/v1/discover/search/"

def request(flow):
    if flow.request.host != 'search-lf.amemv.com':
        return
    elif flow.request.url.startswith(kw_search_user_url):
        # 控制台打印请求的url
        info(flow.request.url)

def response(flow):
    try:
        # info(str(json.loads(flow.response.text)))
        respon = json.loads(flow.response.text)
        keyword = respon['input_keyword']  # 输入的关键词
        for user in respon['user_list']:
            user_info = user['user_info']
            id = user_info['unique_id']  # 抖音id
            nickname = user_info['nickname']  # 抖音昵称
            follower_count = user_info['follower_count']
            chat_user = db.query(ChatInfo).filter_by(chat_douyin_id=id).first()
            if chat_user == None:
                chat_user = ChatInfo()
                chat_user.keyword = keyword
                chat_user.chat_douyin_id = id
                chat_user.chat_douyin_name = nickname
                chat_user.fans_num = follower_count
                db.add(chat_user)
                db.commit()
                db.close()
            else:
                pass
    except:
        pass

