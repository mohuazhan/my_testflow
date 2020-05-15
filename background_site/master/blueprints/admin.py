# coding=utf-8

from flask import Blueprint, flash, render_template, session, request, url_for, jsonify, redirect
from master.extensions import admin, db
from master.models import TaskInfo, DeviceInfo, AccountInfo, \
                            KeywordInfo, ChatInfo,VideoInfo, \
                            WbAccountImport, DyAccountImport, AccountSetup, \
                            LimitSetup, KeywordSetup, ChatSetup
from master.utils import today_min, install_douyin, install_yosemite, \
                            install_weibo, log_on, change_task, \
                            stop_app, import_weibo_account, import_douyin_account, \
                            login_weibo

from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.actions import action
import requests
import asyncio
import datetime
import nest_asyncio


# 这里不能用admin，否则会和flask_admin的admin重名
admin_bp = Blueprint('admin_bk', __name__)

nest_asyncio.apply()
loop = asyncio.get_event_loop()

@admin_bp.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('account.html')
    else:
        user = request.form.get('user')
        pwd = request.form.get('pwd')
        if user == 'xiaomo' and pwd == 'autody@2020@':
            session['user'] = user
            return jsonify({"code": 200, "error": ""})
        else:
            return jsonify({"code": 401, "error": "用户名或密码错误"})

@admin_bp.route('/logout')
def logout():
    del session['user']
    return redirect(url_for('admin_bk.login'))


# 自定义admin界面中的首页，这里不用再新注册视图
class IndexView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')


# 定义模型TaskInfo的admin后台
class TaskInfoAdmin(ModelView):
    column_labels = dict(
        task='任务',
        start_time='执行时间')

    # 禁用某些CRUD操作
    can_create = False
    can_edit = False
    can_delete = False

    @action('执行任务', '执行任务', '确定执行任务？')
    def update_devices(self, ids):
        # 如果id数量不为1，则提示只选'更新设备列表'
        if len(ids) == 1:
            for id in ids:
                # 根据id查询任务名
                res = TaskInfo.query.filter_by(id=id).first()
                if res.task == '更新设备列表':
                    requests.get("http://127.0.0.1:8090/api/cmd/adb/devices")
                    # 插入执行时间
                    res.start_time = datetime.datetime.now()
                    # flash有success，warning，error等提示
                    flash('设备列表已更新完成', 'success')
                elif res.task == '模拟器自动搜关键词':
                    dev_list = []
                    dev_list.append({'dev': '127.0.0.1:7555', 'task': '搜关键词'})
                    loop.run_until_complete(change_task(dev_list))
                    res.start_time = datetime.datetime.now()
                    flash('任务已开始执行,请确保以下四点：1.打开模拟器且运行mitmdump；\
                        2.WLAN挂上mitmdump代理；3.已安装mitmproxy-ca-cert.pem证书；\
                        4.模拟器已安装抖音', 'success')
                elif res.task == '所有设备自动养号':
                    devs = DeviceInfo.query.filter_by(status='已连接').all()
                    try:
                        dev_list = []
                        for dev in devs:
                            dev_list.append({'dev': dev.device_id, 'task': '养号'})
                            # 设备初次启动时设今日和总启动次数为1
                            if dev.start_time == None:
                                dev.start_times_td = 1
                                dev.start_times_all = 1
                            # 当天初次启动时设今日启动次数为1
                            elif dev.start_time < today_min():
                                dev.start_times_td = 1
                            else:
                                dev.start_times_td += 1
                                dev.start_times_all += 1
                            dev.start_time = datetime.datetime.now()
                            dev.task_now = '养号'
                        loop.run_until_complete(change_task(dev_list))
                        res.start_time = datetime.datetime.now()
                        flash('所有设备已开始自动养号', 'success')
                    except:
                        flash('当前未有设备连接，请检查设备是否断开连接', 'error')
                elif res.task == '所有设备自动私信':
                    devs = DeviceInfo.query.filter_by(status='已连接').all()
                    try:
                        dev_list = []
                        for dev in devs:
                            dev_list.append({'dev': dev.device_id, 'task': '私信'})
                            # 设备初次启动时设今日和总启动次数为1
                            if dev.start_time == None:
                                dev.start_times_td = 1
                                dev.start_times_all = 1
                            # 当天初次启动时设今日启动次数为1
                            elif dev.start_time < today_min():
                                dev.start_times_td = 1
                            else:
                                dev.start_times_td += 1
                                dev.start_times_all += 1
                            dev.start_time = datetime.datetime.now()
                            dev.task_now = '私信'
                        loop.run_until_complete(change_task(dev_list))
                        res.start_time = datetime.datetime.now()
                        flash('所有设备已开始自动私信', 'success')
                    except:
                        flash('当前未有设备连接，请检查设备是否断开连接', 'error')
                db.session.commit()
                db.session.close()
        else:
            flash('请勿多选任务项', 'warning')


# 定义模型DeviceInfo的admin后台
class DeviceInfoAdmin(ModelView):
    column_labels = dict(
        device_id='设备串号',
        douyin_name='当前抖音号',
        task_now='当前(或最近一次)任务',
        task_pid='当前(或最近一次)任务进程pid',
        start_times_td='今天启动任务次数',
        start_times_all='启动任务总次数',
        status='状态',
        start_time='启动时间')

    # 禁用某些CRUD操作
    can_create = False
    can_edit = False
    can_delete = False
    # 将添加和编辑表单显示在列表页面的模式窗口中，而不是专用的创建和编辑页面
    create_modal = False
    edit_modal = False
    # 如果未应用排序，则为默认排序列,使用元组来控制升序
    column_default_sort = ('status', True)
    # 分页的默认页面大小
    page_size = 10
    # 允许通过下拉列表选择页面大小
    can_set_page_size = True
    # 要启用模型视图的csv导出
    can_export = False
    # 搜索列表
    column_searchable_list = ['device_id', 'douyin_name', 'task_now']

    # 在批处理函数前加abcd命名是为了从上到下排序
    @action('安装抖音', '安装抖音', '确定执行安装？')
    def a1_install_douyin(self, ids):
        dev_list = []
        for id in ids:
            # 根据id查询设备串号
            res = DeviceInfo.query.filter_by(id=id).first()
            # 如果设备已连接则将串号加入列表
            if res.status == '已连接':
                dev_list.append(res.device_id)
                # 设备初次启动时设今日和总启动次数为1
                if res.start_time == None:
                    res.start_times_td = 1
                    res.start_times_all = 1
                # 当天初次启动时设今日启动次数为1
                elif res.start_time < today_min():
                    res.start_times_td = 1
                else:
                    res.start_times_td += 1
                    res.start_times_all += 1
                res.start_time = datetime.datetime.now()
                res.task_now = '安装抖音'
                db.session.commit()
                db.session.close()
            else:
                pass
        if dev_list == []:
            flash('请选择已连接的设备', 'error')
        else:
            loop.run_until_complete(install_douyin(dev_list))
            flash('已开始执行安装', 'success')

    @action('安装Yosemite', '安装Yosemite', '确定执行安装？')
    def a2_install_douyin(self, ids):
        dev_list = []
        for id in ids:
            # 根据id查询设备串号
            res = DeviceInfo.query.filter_by(id=id).first()
            # 如果设备已连接则将串号加入列表
            if res.status == '已连接':
                dev_list.append(res.device_id)
                # 设备初次启动时设今日和总启动次数为1
                if res.start_time == None:
                    res.start_times_td = 1
                    res.start_times_all = 1
                # 当天初次启动时设今日启动次数为1
                elif res.start_time < today_min():
                    res.start_times_td = 1
                else:
                    res.start_times_td += 1
                    res.start_times_all += 1
                res.start_time = datetime.datetime.now()
                res.task_now = '安装Yosemite'
                db.session.commit()
                db.session.close()
            else:
                pass
        if dev_list == []:
            flash('请选择已连接的设备', 'error')
        else:
            loop.run_until_complete(install_yosemite(dev_list))
            flash('已开始执行安装', 'success')

    @action('安装微博', '安装微博', '确定执行安装？')
    def a3_install_weibo(self, ids):
        dev_list = []
        for id in ids:
            # 根据id查询设备串号
            res = DeviceInfo.query.filter_by(id=id).first()
            # 如果设备已连接则将串号加入列表
            if res.status == '已连接':
                dev_list.append(res.device_id)
                # 设备初次启动时设今日和总启动次数为1
                if res.start_time == None:
                    res.start_times_td = 1
                    res.start_times_all = 1
                # 当天初次启动时设今日启动次数为1
                elif res.start_time < today_min():
                    res.start_times_td = 1
                else:
                    res.start_times_td += 1
                    res.start_times_all += 1
                res.start_time = datetime.datetime.now()
                res.task_now = '安装微博'
                db.session.commit()
                db.session.close()
            else:
                pass
        if dev_list == []:
            flash('请选择已连接的设备', 'error')
        else:
            loop.run_until_complete(install_weibo(dev_list))
            flash('已开始执行安装', 'success')

    @action('批量登录微博', '批量登录微博', '确定执行批量登录？')
    def b_change_account(self, ids):
        dev_list = []
        for id in ids:
            # 根据id查询设备串号
            res = DeviceInfo.query.filter_by(id=id).first()
            if res.status == '已连接':
                dev_list.append(res.device_id)
                # 设备初次启动时设今日和总启动次数为1
                if res.start_time == None:
                    res.start_times_td = 1
                    res.start_times_all = 1
                # 当天初次启动时设今日启动次数为1
                elif res.start_time < today_min():
                    res.start_times_td = 1
                else:
                    res.start_times_td += 1
                    res.start_times_all += 1
                res.start_time = datetime.datetime.now()
                res.task_now = '批量登录微博'
                db.session.commit()
                db.session.close()
            else:
                pass
        if dev_list == []:
            flash('请选择已连接的设备', 'error')
        else:
            loop.run_until_complete(login_weibo(dev_list))
            flash('已开始执行微博账号批量登录', 'success')

    @action('切换抖音号', '切换抖音号', '确定执行切换？')
    def c_change_account(self, ids):
        dev_list = []
        for id in ids:
            # 根据id查询设备串号
            res = DeviceInfo.query.filter_by(id=id).first()
            if res.status == '已连接':
                dev_list.append(res.device_id)
            else:
                pass
        if dev_list == []:
            flash('请选择已连接的设备', 'error')
        else:
            loop.run_until_complete(log_on(dev_list))
            flash('已开始执行账号登录切换', 'success')

    @action('批量养号', '批量养号', '确定批量养号？')
    def d1_train_account(self, ids):
        dev_list = []
        for id in ids:
            # 根据id查询设备串号
            res = DeviceInfo.query.filter_by(id=id).first()
            if res.status == '已连接':
                dev_list.append({'dev': res.device_id, 'task': '养号'})
                # 设备初次启动时设今日和总启动次数为1
                if res.start_time == None:
                    res.start_times_td = 1
                    res.start_times_all = 1
                # 当天初次启动时设今日启动次数为1
                elif res.start_time < today_min():
                    res.start_times_td = 1
                else:
                    res.start_times_td += 1
                    res.start_times_all += 1
                res.start_time = datetime.datetime.now()
                res.task_now = '养号'
                db.session.commit()
                db.session.close()
            else:
                pass
        if dev_list == []:
            flash('请选择已连接的设备', 'error')
        else:
            loop.run_until_complete(change_task(dev_list))
            flash('已开始批量养号', 'success')

    @action('批量私信', '批量私信', '确定批量私信？')
    def d2_chat_users(self, ids):
        dev_list = []
        for id in ids:
            # 根据id查询设备串号
            res = DeviceInfo.query.filter_by(id=id).first()
            if res.status == '已连接':
                dev_list.append({'dev': res.device_id, 'task': '私信'})
                # 设备初次启动时设今日和总启动次数为1
                if res.start_time == None:
                    res.start_times_td = 1
                    res.start_times_all = 1
                # 当天初次启动时设今日启动次数为1
                elif res.start_time < today_min():
                    res.start_times_td = 1
                else:
                    res.start_times_td += 1
                    res.start_times_all += 1
                res.start_time = datetime.datetime.now()
                res.task_now = '私信'
                db.session.commit()
                db.session.close()
            else:
                pass
        if dev_list == []:
            flash('请选择已连接的设备', 'error')
        else:
            loop.run_until_complete(change_task(dev_list))
            flash('已开始批量私信', 'success')

    @action('终止任务', '终止任务', '确定执行终止？')
    def e_stop_task(self, ids):
        dev_list = []
        for id in ids:
            # 根据id查询设备串号
            res = DeviceInfo.query.filter_by(id=id).first()
            if res.status == '已连接':
                dev_list.append(res.device_id)
                # 将当前任务设为空
                res.task_now = None
                db.session.commit()
                db.session.close()
            else:
                res.task_now = None
                db.session.commit()
                db.session.close()
        if dev_list == []:
            flash('请选择已连接的设备', 'error')
        else:
            loop.run_until_complete(stop_app(dev_list))
            flash('已开始终止各设备当前任务', 'success')


# 定义模型AccountInfo的admin后台
class AccountInfoAdmin(ModelView):
    column_labels = dict(
        douyin_name='抖音号',
        task_now='当前任务',
        online_times_td='上线次数',
        watch_times_td='观看视频数',
        point_times_td='点赞数',
        comment_times_td='评论数',
        chat_times_td='私信人数',
        login_time='登录时间')
    # 列表视图列或添加/编辑表单字段的描述
    column_descriptions = dict(
        online_times_td='该数据为当天的上线次数',
        watch_times_td='该数据为当天的观看视频数',
        point_times_td='该数据为当天的点赞数',
        comment_times_td='该数据为当天的评论数',
        chat_times_td='该数据为当天的私信人数',
    )

    can_create = False
    can_edit = False
    can_delete = False
    page_size = 10
    can_set_page_size = True
    column_searchable_list = ['douyin_name', 'task_now']


# 定义模型KeywordInfo的admin后台
class KeywordInfoAdmin(ModelView):
    column_labels = dict(
        keyword='关键词',
        douyin_name='搜索该词的抖音号',
        status='状态',
        search_time='搜索时间')

    can_create = False
    can_edit = False
    can_delete = False
    page_size = 10
    can_set_page_size = True
    column_searchable_list = ['keyword']


# 定义模型ChatInfo的admin后台
class ChatInfoAdmin(ModelView):
    column_labels = dict(
        chat_douyin_id='私信抖音id',
        chat_douyin_name='私信抖音号',
        douyin_name='联系帐号',
        fans_num='粉丝数',
        keyword='来源关键词',
        status='状态',
        chat_label='私信标签',
        chat_time='私信时间')
    # 列过滤器的集合
    column_filters = ('chat_douyin_name', 'fans_num')

    can_create = False
    can_edit = False
    can_delete = True
    page_size = 10
    can_set_page_size = True
    column_searchable_list = ['chat_douyin_name', 'douyin_name', 'keyword']


# 定义模型ChatSetup的admin后台
class VideoInfoAdmin(ModelView):
    column_labels = dict(
        video_douyin_name='视频作者',
        video_title='视频标题',
        douyin_name='观众',
        point_num='当时点赞数',
        comment_num='当时评论数',
        share_num='当时分享数',
        watch_time='观看时间')
    column_filters = ('point_num', 'comment_num', 'share_num')

    can_create = False
    can_edit = False
    can_delete = False
    page_size = 10
    can_set_page_size = True
    column_searchable_list = ['video_douyin_name', 'video_title']


# 定义模型WbAccountImport的admin后台
class WbAccountImportAdmin(ModelView):
    column_labels = dict(
        account_text='批量导入帐号文本',
        status='状态')
    # 列表视图列或添加/编辑表单字段的描述
    column_descriptions = dict(
        account_text=\
        '''
        微博账号批量导入的文本格式如：
        15243737561----hkpmrl748
        15211681243----segrtx984
        18817190296----ojdqbz050
        ×××××××××××----×××××××××
        '''
    )

    # 列表视图列格式化程序字典
    # 这里account_text的文本显示过长，现在只显示前50个字符即可
    column_formatters = dict(account_text=lambda v, c, m, p: m.account_text[0:80]+str('  ......'))
    '''
    回调函数具有原型：
    def formatter(view, context, model, name):
        # `view` is current administrative view
        # `context` is instance of jinja2.runtime.Context
        # `model` is model instance
        # `name` is property name
        pass
    正好和上面的v, c, m, p相对应
    '''
    # 将此设置为true将启用详细信息视图
    can_view_details=True
    # 列表视图列格式化程序的字典，用于详细信息视图，这里让account_text在详细视图中正常显示
    column_formatters_detail = dict(
        account_text=lambda v, c, m, p: m.account_text,
        status=lambda v, c, m, p: m.status)
    # 使字段只读
    form_widget_args = {
        'status':{'disabled':True}
    }
    create_modal = True
    edit_modal = True
    page_size = 10

    @action('批量导入', '批量导入', '确定批量导入账号？')
    def import_weibo_acc(self, ids):
        id_list = []
        for id in ids:
            res = WbAccountImport.query.filter_by(id=id).first()
            # 如果账号导入表中的状态为None，则添加导入
            if res.status == None:
                id_list.append(res.id)
            else:
                pass
        if id_list == []:
            flash('请选择未导入的批量账号文本', 'error')
        else:
            loop.run_until_complete(import_weibo_account(id_list))
            flash('已开始批量导入', 'success')

# 定义模型DyAccountImport的admin后台
class DyAccountImportAdmin(ModelView):
    column_labels = dict(
        account_text='批量导入帐号文本',
        status='状态')
    # 列表视图列或添加/编辑表单字段的描述
    column_descriptions = dict(
        account_text=\
        '''
        抖音账号批量导入的文本格式如：
        ﻿2894742776http://×××.××.×××.×××
        ﻿﻿﻿2894734293http://×××.××.×××.×××
        ﻿﻿﻿2894733171http://×××.××.×××.×××
        ﻿﻿﻿2894733194http://×××.××.×××.×××
        '''
    )

    # 列表视图列格式化程序字典
    # 这里account_text的文本显示过长，现在只显示前50个字符即可
    column_formatters = dict(account_text=lambda v, c, m, p: m.account_text[0:80]+str('  ......'))
    # 将此设置为true将启用详细信息视图
    can_view_details=True
    # 列表视图列格式化程序的字典，用于详细信息视图，这里让account_text在详细视图中正常显示
    column_formatters_detail = dict(
        account_text=lambda v, c, m, p: m.account_text,
        status=lambda v, c, m, p: m.status)
    # 使字段只读
    form_widget_args = {
        'status':{'disabled':True}
    }
    create_modal = True
    edit_modal = True
    page_size = 10

    @action('批量导入', '批量导入', '确定批量导入账号？')
    def import_douyin_acc(self, ids):
        id_list = []
        for id in ids:
            res = DyAccountImport.query.filter_by(id=id).first()
            # 如果账号导入表中的状态为None，则添加导入
            if res.status == None:
                id_list.append(res.id)
            else:
                pass
        if id_list == []:
            flash('请选择未导入的批量账号文本', 'error')
        else:
            loop.run_until_complete(import_douyin_account(id_list))
            flash('已开始批量导入', 'success')

# 定义模型AccountSetup的admin后台
class AccountSetupAdmin(ModelView):
    column_labels = dict(
        username='用户名(如抖音名,微博名)',
        device_id='所在设备串号',
        account='账号',
        password='密码(或验证码url)',
        new_password='重新设置的密码',
        platform='第三方平台',
        status='状态')
    column_filters = ('device_id', 'platform')

    # 指定选择选项列表来限制文本字段的可能值
    form_choices = {
        'status': [
            ('启用', '启用'),
            ('禁用', '禁用')
        ],
        'platform': [
            ('微博', '微博'),
            ('抖音', '抖音')
        ]
    }
    # 使字段只读
    form_widget_args = {
        'douyin_name':{'disabled':True}
    }
    # 获得更快的编辑体验，在列表视图中启用内联编辑：
    column_editable_list = ['device_id', 'new_password', 'status']
    create_modal = True
    edit_modal = True
    page_size = 10
    column_searchable_list = ['username', 'account']
    # 允许模型列表导出
    can_export = True


# 定义模型LimitSetup的admin后台
class LimitSetupAdmin(ModelView):
    column_labels = dict(
        limit_option='限制项',
        limit_times='限制数')

    # 使字段只读
    form_widget_args = {
        'limit_option':{'disabled':True}
    }
    can_create = False
    can_edit = True
    can_delete = False
    column_editable_list = ['limit_times']


# 定义模型KeywordSetup的admin后台
class KeywordSetupAdmin(ModelView):
    column_labels = dict(
        keyword='关键词',
        status='状态')

    # 使字段只读
    form_widget_args = {
        'status':{'disabled':True}
    }
    create_modal = True
    edit_modal = True
    page_size = 10
    column_searchable_list = ['keyword']


# 定义模型ChatSetup的admin后台
class ChatSetupAdmin(ModelView):
    column_labels = dict(
        chat_label='私信标签',
        chat_content='私信内容',
        status='状态')

    form_choices = {
        'status': [
            ('启用', '启用'),
            ('禁用', '禁用'),
        ]
    }
    column_editable_list = ['status']
    create_modal = True
    edit_modal = True
    page_size = 10
    column_searchable_list = ['chat_content']


# 在admin界面注册视图
admin.add_view(TaskInfoAdmin(TaskInfo, db.session, name='任务管理'))
admin.add_view(DeviceInfoAdmin(DeviceInfo, db.session, name='设备管理'))
admin.add_view(AccountInfoAdmin(AccountInfo, db.session, name='账号信息表'))
admin.add_view(KeywordInfoAdmin(KeywordInfo, db.session, name='关键词信息表'))
admin.add_view(ChatInfoAdmin(ChatInfo, db.session, name='私信信息表'))
admin.add_view(VideoInfoAdmin(VideoInfo, db.session, name='视频信息表'))
admin.add_view(WbAccountImportAdmin(WbAccountImport, db.session, name='微博账号批量导入', category="项目设置"))
admin.add_view(DyAccountImportAdmin(DyAccountImport, db.session, name='抖音账号批量导入', category="项目设置"))
admin.add_view(AccountSetupAdmin(AccountSetup, db.session, name='账号设置', category="项目设置"))
admin.add_view(LimitSetupAdmin(LimitSetup, db.session, name='限制项设置', category="项目设置"))
admin.add_view(KeywordSetupAdmin(KeywordSetup, db.session, name='关键词设置', category="项目设置"))
admin.add_view(ChatSetupAdmin(ChatSetup, db.session, name='私信设置', category="项目设置"))

