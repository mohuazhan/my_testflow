# coding=utf-8

from settings import PYTHON_PATH,ADB_PATH
from crud import *
from database import SessionLocal

from fastapi import APIRouter
import subprocess
from sqlalchemy.orm import scoped_session

router = APIRouter()
# 调用了scoped_session_maker.remove()后
# 再用scoped_session_maker()创建的session对象和之前创建的就是不同的对象了
db = scoped_session(SessionLocal)

# 更新设备列表到数据库
@router.get("/devices")
async def adb_device():
    # 查看当前连接调试的设备
    adb_cmd = subprocess.Popen('%s devices'%ADB_PATH,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True)
    # 按行读取cmd结果
    devices = adb_cmd.stdout.readlines()
    adb_cmd.stdout.close()
    # 重置所有设备为断开
    update_dev_status(db)
    # 将设备串号逐个插入数据库
    res_list = []
    for dev in devices:
        # cmd结果筛选,需要注意的是dev类型为字节而非字符串
        if bytes('device', encoding="utf8") in dev \
            and bytes('List of devices', encoding="utf8") not in dev \
                and bytes('127.0.0.1:7555', encoding="utf8") not in dev:
            # 字节截取
            dev = dev.split(b'\tdevice\r\n')[0]
            res = update_device(db, dev)
            res_list.append(res)
        else:pass
    # 这步非常关键！删除会话后，下次请求将不会从缓存中读取
    db.remove()

    return res_list
