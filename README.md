# 抖音自动化测试项目

## 项目备注
- 注意事项
	* 运行在win10
	* 基于python3.6，MySQL8.0
	* 统一安装相同版本的抖音和微博APP
	* 每台手机通过该系统安装抖音后，可以事先手动操作，例如手动私信一个用户来跳过安装多闪的提示
	* 本项目使用的点位操作较多，所兼容机型为OPPO A59s
	* OPPO手机设置：开发者选项的最底部，勾选 禁止监控权限；其他设置中找到应用程序管理，将抖音权限管理中的打开或关闭移动数据，WLAN网络和蓝牙等改为禁止，其他项改为禁止或允许，切勿为询问
	* 手机需用户登录（如华为账号，OPPO账号等）
	* 手机需打开USB调试，并允许一律在工作机调试
	* 千万别更新抖音，如需更新或兼容其他机型，请与开发者联系
	* 手机兼容性问题可参考：[设备兼容性](http://airtest.netease.com/docs/docs_AirtestIDE-zh_CN/2_device_connection/2_android_faq.html#id7)
	* 在 v1.0.3 中确定使用已绑定手机号的抖音号账号密码直登，在此前需要将各手机号接码完成初次登录，然后修改各个账号的密码并设置昵称，并在账号设置表中填写该账号的新密码和登录时的设备串号，因为抖音号如果频繁更换设备登录，那么即便用账号密码直登也要再次接码

- 常见问题
	* ADB连接相关
		> *如何打开开发者选项？*  
		打开「关于手机」，连续点击「版本号」7次
		
		> *adb server version (39) doesn't match this client (40); killing...*  
		原因：airtest中的adb.exe版本与Android Studio中的adb版本冲突产生  
		解决方法：用Android Studio中的adb替换airtest中的adb
		
	* python相关
		> *pymysql\cursors.py:170: Warning: (1366, "Incorrect string value: '***' for column 'VARIABLE_VALUE' at row 1")*  
		解决办法：pip install mysql-connector-python  
		然后将：
		engine = create_engine('mysql+pymysql://username:password@localhost:3306/auto_dy?charset=utf8mb4')  
		改为：
		engine = create_engine('mysql+mysqlconnector://username:password@localhost:3306/auto_dy?charset=utf8mb4')  
		
		> *遇到线程阻塞撑爆CPU*  
		解决方法：在终端执行taskkill /F /IM python.exe


## 项目说明

### mitmproxy抓包抖音app

由于通过真机搜索关键词获取UI树来得到用户信息的效率低且不稳定，因此我选用了mitmdump+airtest来搜索关键词获取用户信息

**配置步骤**
1. 现在用fiddler真机抓包抖音app已经难以实现，这里可以使用安卓模拟器（MUMU模拟器）  
2. 模拟器先开启root权限并打开USB调试，下载并先后安装XposedInstaller和JustTrustMe（apk已放在/my-testflow/mitmdump_collector/app下），安装前记得到设置——>应用兼容性，将兼容性关闭
3. 安装好XposedInstaller后打开，在Version89处选择安装Xposed
4. 然后点击左上角，到模块处勾选JustTrustMe，然后退出XposedInstaller即可
5. 此时到设置——>应用兼容性，将兼容性打开
6. 安装pip install mitmproxy -i https://pypi.tuna.tsinghua.edu.cn/simple
7. 下载使用基于用户定义策略的条件TLS拦截的脚本tls_passthrough.py（已放在mitmdump_collector下），并将tls_passthrough.py放到C:\Users\91965\AppData\Local\Programs\Python\Python36\Scripts下
8. mitmproxy的证书位于C:\Users\91965\.mitmproxy下，将其中的mitmproxy-ca-cert.pem放到C:\Users\91965\Documents\MuMu共享文件夹下，并在MUMU模拟器中安装证书
9. 在cmd中启动mitmweb：  
	C:\Users\91965\AppData\Local\Programs\Python\Python36\Scripts>mitmweb -p 8989 -s tls_passthrough.py  
	Web server listening at http://127.0.0.1:8081/  
	Loading script tls_passthrough.py  
	Proxy server listening at http://*:8989  
10. 在MUMU模拟器中打开WLAN，左键长按已连接的WLAN，手动挂上代理
11. 在主机浏览器中打开http://127.0.0.1:8081/即可查看抓包的内容
12. 其实第9步可以忽略，直接mitmweb -p 8989/mitmdump -p 8989也能抓包到APP，当时在真机上抓包才用的这步，另外，每一次更换IP都需要在MUMU模拟器重新安装mitmproxy-ca-cert.pem证书


## 项目部署教程

1. 安装完MySQL8.0后创建auto_dy库，charset为utf8mb4，collation为utf8mb4_0900_ai_ci  

2. 安装python依赖包：
```
C:\Users\Administrator>pip install -e D:\auto_douyin\my-testflow -i https://pypi.tuna.tsinghua.edu.cn/simple
```
3. 修改background_site/master/settings.py, control_api/database.py, mitmdump_collector/database.py中的MySQL设置  

4. 修改control_api/settings.py中的python和adb路径; 如果是在cmd运行代码文件，须修改control_api/routers/testflow/utils.py中app和img的路径为绝对路径  

5. 如果MUMU模拟器不管用（如出现抖音需要登录，安装证书需要凭据存储密码等），可以使用夜神模拟器，记得将background_site/master/blueprints/admin.py和control_api/routers/v1/adb.py中的127.0.0.1:7555改为127.0.0.1:62001，详细请见：[Android模拟器连接](http://airtest.netease.com/docs/docs_AirtestIDE-zh_CN/2_device_connection/3_emulator_connection.html#id1)  

6. 先后运行background_site/manage.py，control_api/main.py，mitmdump_collector/douyin_kw_search.py，在浏览器打开 http://127.0.0.1:8080/admin (后台账号密码在background_site/master/blueprints/admin.py中)进入管理后台，打开 http://127.0.0.1:8090/docs 查看api文档  


## 操作步骤

### 抖音 (切换账号，养号，私信，搜关键词)

1. 卸载手机上原有的抖音和微博等app；
2. 手机通过USB连接电脑并打开USB调试，在「任务管理」中执行 更新设备列表；
3. 在「设备管理」中多选设备，为每台已连接的设备安装抖音和yosimite；
4. 在「项目设置」中打开抖音账号批量导入，创建新的记录，将批量账号的文本复制粘贴到文本框中，点击保存即可导入；
5. 在「项目设置」中打开账号设置，可查看已导入的账号，此时需要为每个抖音账号编辑其所登录的设备和重置的密码；
6. 在「项目设置」中打开限制项设置，关键词设置和私信设置，为每项添加设置；
7. 在「设备管理」中为每个已连接的设备执行养号，私信等任务，终止任务的功能暂不可用，如需暂停某台设备当前任务，可将USB断开后再次连上，并重新更新设备列表

## 版本概览

| 版本号 | 项目进度 |
|-- |-- |
| v1.0.0 | 已完成抖音自动化：养号(真机),搜关键词(模拟器),私信(真机) |
|  | 待完成：抖音账号自动切换 |
| v1.0.1 | 设备管理新增：安装Yosemite |
|  | 新增：私信时加入搜索用户不存在或私密账户等情况处理 |
|  | 修改：养号和私信时遇到特殊情况重启抖音继续操作，而不是用return None停止操作 |
| v1.0.2 | 设备管理新增：安装微博，批量登录微博 |
|  | 项目设置新增：微博账号批量导入，抖音账号批量导入，限制项设置 |
| v1.0.3 | 兼容的抖音版本升级为10.9 |
|  | 设备管理功能完善：切换抖音号 |
|  | 账号设置新增：所在设备串号和重置密码编辑 |
|  | 养号时poco抓取不到视频作者的抖音昵称，统一设为'未知' |
|  | 在 /res/doc/ 下添加了测试账号文本文件 |
|  | 新增：设定log级别，取消airtest脚本执行过程中刷新大量的log信息 |
| v1.0.4 | 设备管理新增：当前(或最近一次)任务进程pid(字段:task_pid)，并完善终止任务功能(根据pid杀死进程) |