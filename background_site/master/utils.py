# coding=utf-8

import aiohttp
import asyncio
import datetime

install_dy_url = 'http://127.0.0.1:8090/api/douyin/tasks/install_douyin/{dev}'
install_ym_url = 'http://127.0.0.1:8090/api/douyin/tasks/install_yosemite/{dev}'
install_wb_url = 'http://127.0.0.1:8090/api/weibo/tasks/install_weibo/{dev}'
login_dy_url = 'http://127.0.0.1:8090/api/douyin/tasks/login_account/{dev}'
task_url = 'http://127.0.0.1:8090/api/douyin/tasks/change_task/{dev}/{task}'
stop_url = 'http://127.0.0.1:8090/api/douyin/tasks/stop_app/{dev}'
import_wb_acc_url = 'http://127.0.0.1:8090/api/weibo/tasks/import_account/{id}'
import_dy_acc_url = 'http://127.0.0.1:8090/api/douyin/tasks/import_account/{id}'
login_wb_url = 'http://127.0.0.1:8090/api/weibo/tasks/login_account/{dev}'

# 获取当天零点的时间
def today_min():
    today = datetime.datetime.today()
    return datetime.datetime(today.year, today.month, today.day, 0, 0, 0)


async def get_1(session, queue, base_url):
    while True:
        try:
            dev = queue.get_nowait()
        except asyncio.QueueEmpty:
            return
        if '{dev}' in base_url:
            url = base_url.format(dev=dev)
        if '{id}' in base_url:
            url = base_url.format(id=dev)
        resp = await session.get(url)
        # print(await resp.text(encoding='utf-8'))

async def get_2(session, queue, base_url):
    while True:
        try:
            dev = queue.get_nowait()
        except asyncio.QueueEmpty:
            return
        url = base_url.format(dev=dev['dev'],task=dev['task'])
        resp = await session.get(url)

# 安装抖音
async def install_douyin(dev_list):
    async with aiohttp.ClientSession() as session:
        queue = asyncio.Queue()
        for dev in dev_list:
            queue.put_nowait(dev)
        tasks = []
        for _ in range(len(dev_list)):
            task = get_1(session, queue, install_dy_url)
            tasks.append(task)
        await asyncio.wait(tasks)

# 安装Yosemite
async def install_yosemite(dev_list):
    async with aiohttp.ClientSession() as session:
        queue = asyncio.Queue()
        for dev in dev_list:
            queue.put_nowait(dev)
        tasks = []
        for _ in range(len(dev_list)):
            task = get_1(session, queue, install_ym_url)
            tasks.append(task)
        await asyncio.wait(tasks)

# 安装微博
async def install_weibo(dev_list):
    async with aiohttp.ClientSession() as session:
        queue = asyncio.Queue()
        for dev in dev_list:
            queue.put_nowait(dev)
        tasks = []
        for _ in range(len(dev_list)):
            task = get_1(session, queue, install_wb_url)
            tasks.append(task)
        await asyncio.wait(tasks)

# 登录账号
async def log_on(dev_list):
    async with aiohttp.ClientSession() as session:
        queue = asyncio.Queue()
        for dev in dev_list:
            queue.put_nowait(dev)
        tasks = []
        for _ in range(len(dev_list)):
            task = get_1(session, queue, login_dy_url)
            tasks.append(task)
        await asyncio.wait(tasks)

# 切换任务
async def change_task(dev_list):
    async with aiohttp.ClientSession() as session:
        queue = asyncio.Queue()
        for dev in dev_list:
            queue.put_nowait(dev)
        tasks = []
        for _ in range(len(dev_list)):
            task = get_2(session, queue, task_url)
            tasks.append(task)
        await asyncio.wait(tasks)

# 终止任务
async def stop_app(dev_list):
    async with aiohttp.ClientSession() as session:
        queue = asyncio.Queue()
        for dev in dev_list:
            queue.put_nowait(dev)
        tasks = []
        for _ in range(len(dev_list)):
            task = get_1(session, queue, stop_url)
            tasks.append(task)
        await asyncio.wait(tasks)

# 批量导入微博账号
async def import_weibo_account(id_list):
    async with aiohttp.ClientSession() as session:
        queue = asyncio.Queue()
        for id in id_list:
            queue.put_nowait(id)
        tasks = []
        for _ in range(len(id_list)):
            task = get_1(session, queue, import_wb_acc_url)
            tasks.append(task)
        await asyncio.wait(tasks)

# 批量导入抖音账号
async def import_douyin_account(id_list):
    async with aiohttp.ClientSession() as session:
        queue = asyncio.Queue()
        for id in id_list:
            queue.put_nowait(id)
        tasks = []
        for _ in range(len(id_list)):
            task = get_1(session, queue, import_dy_acc_url)
            tasks.append(task)
        await asyncio.wait(tasks)

# 批量登录微博
async def login_weibo(dev_list):
    async with aiohttp.ClientSession() as session:
        queue = asyncio.Queue()
        for dev in dev_list:
            queue.put_nowait(dev)
        tasks = []
        for _ in range(len(dev_list)):
            task = get_1(session, queue, login_wb_url)
            tasks.append(task)
        await asyncio.wait(tasks)