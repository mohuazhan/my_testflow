# coding=utf-8
'''
自动化脚本笔记
'''
from airtest.core.api import *
# 根据设备串号连接设备
dev = connect_device('Android:///MJEQOR5H75BY45SS')
# 获取当前设备
from airtest.core.android.android import Android
# dev = device()
# 打印出手机上安装的所有App的package name
# 默认参数为false，当third_only=True时，
# 打印出手机上安装的所有第三方App 的package name
print(dev.list_app(third_only=True))
# 启动应用程序
start_app('com.ss.android.ugc.aweme')
# 检查package是否在手机上，存在则返回True，否则报错
# dev.check_app('com.ss.android.ugc.aweme')
# 终止应用程序
stop_app('com.ss.android.ugc.aweme')
# 在设备上安装应用程序，replace默认为False，为True时意为替换已存在的App
dev.install_app("res/app/com.ss.android.ugc.aweme.apk", replace=True)

