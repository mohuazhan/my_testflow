# coding=utf-8

from .scripts import check_install_douyin, check_install_yosemite, login_douyin, change_task, stop_douyin, import_douyin_acc

from multiprocessing import Process
from fastapi import APIRouter
import time

router = APIRouter()

# 安装抖音
@router.get("/install_douyin/{device_id}")
async def install_app_dy(device_id: str):
    # 开启一个进程异步处理事件
    p = Process(target=check_install_douyin,args=(device_id,))
    p.start()

# 安装Yosemite
@router.get("/install_yosemite/{device_id}")
async def install_app_ym(device_id: str):
    p = Process(target=check_install_yosemite,args=(device_id,))
    p.start()

# 登录抖音号
@router.get("/login_account/{device_id}")
async def login_account(device_id: str):
    p = Process(target=login_douyin,args=(device_id,))
    p.start()

# 切换任务
@router.get("/change_task/{device_id}/{task}")
async def change_duty(device_id: str, task: str):
    p = Process(target=change_task,args=(device_id,task,))
    p.start()

# 终止任务
@router.get("/stop_app/{device_id}")
async def stop_task(device_id: str):
    p = Process(target=stop_douyin,args=(device_id,))
    p.start()

# 批量导入账号
@router.get("/import_account/{id}")
async def import_account(id: int):
    p = Process(target=import_douyin_acc,args=(id,))
    p.start()