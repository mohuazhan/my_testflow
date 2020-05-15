# coding=utf-8

from crud import *
from database import SessionLocal
from .scripts import check_install_weibo, import_weibo_acc, login_weibo

from multiprocessing import Process
from fastapi import APIRouter
import time
import subprocess
from sqlalchemy.orm import scoped_session

router = APIRouter()
db = scoped_session(SessionLocal)

# 当执行新的任务时，杀死旧进程，插入新进程pid
def reset_task(device_id, task_pid):
    # 获取当前任务进程pid，如果pid为空则跳过，否则根据pid强制杀死进程
    pid_exists = get_task_pid(db, device_id)
    if pid_exists == None:
        pass
    else:
        kill_process = subprocess.Popen('taskkill /F /pid:%s'% pid_exists,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True)
    # 重置当前任务进程pid
    reset_task_pid(db, device_id, task_pid)

# 安装微博
@router.get("/install_weibo/{device_id}")
async def install_app_dy(device_id: str):
    # 开启一个进程异步处理事件
    p = Process(target=check_install_weibo,args=(device_id,))
    p.start()
    task_pid = p.pid
    reset_task(device_id, task_pid)

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
    task_pid = p.pid
    reset_task(device_id, task_pid)