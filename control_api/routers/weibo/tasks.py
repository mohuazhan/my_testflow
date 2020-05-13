# coding=utf-8

from .scripts import check_install_weibo, import_weibo_acc, login_weibo

from multiprocessing import Process
from fastapi import APIRouter
import time

router = APIRouter()

# 安装微博
@router.get("/install_weibo/{device_id}")
async def install_app_dy(device_id: str):
    # 开启一个进程异步处理事件
    p = Process(target=check_install_weibo,args=(device_id,))
    p.start()

# 批量导入账号
@router.get("/import_account/{id}")
async def import_account(id: int):
    p = Process(target=import_weibo_acc,args=(id,))
    p.start()

# 批量登录账号
@router.get("/login_account/{device_id}")
async def login_account(device_id: str):
    p = Process(target=login_weibo,args=(device_id,))
    p.start()