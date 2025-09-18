from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import re
import random
import datetime
import bcrypt
import json
import client

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # 用于会话安全

# 获取格式化的时间字符串
def get_formatted_timestamp():
    now = datetime.datetime.now()
    # 今天的时间格式: 时:分
    if now.date() == datetime.datetime.now().date():
        return now.strftime("%H:%M")
    # 昨天的格式: 昨天 时:分
    elif now.date() == (datetime.datetime.now() - datetime.timedelta(days=1)).date():
        return "昨天 " + now.strftime("%H:%M")
    # 本周内的格式: 星期X 时:分
    elif now.isocalendar()[1] == datetime.datetime.now().isocalendar()[1]:
        weekdays = ["一", "二", "三", "四", "五", "六", "日"]
        return f"周{weekdays[now.weekday()]} {now.strftime('%H:%M')}"
    # 其他时间: 月/日 时:分
    else:
        return now.strftime("%m/%d %H:%M")


# 获取历史记录时间标签
def get_time_label(timestamp):
    now = datetime.datetime.now()
    diff = now - timestamp

    if diff.days == 0:
        if diff.seconds < 60:
            return "刚刚"
        elif diff.seconds < 3600:
            return f"{diff.seconds // 60}分钟前"
        else:
            return "今天"
    elif diff.days == 1:
        return "昨天"
    elif diff.days < 7:
        return f"{diff.days}天前"
    elif diff.days < 30:
        weeks = diff.days // 7
        return f"{weeks}周前"
    else:
        # return timestamp.strftime("%Y/%m/%d")
        return "很久以前"


# 创建对话函数
def create_chat(user_id, title=None):
    if(title==None):
        title="未命名对话"
    
    array=['db','chatdb','add_chat',user_id,title]
    res=client.send_array_to_server(array)
    chat = {
        "chat_id": res,
        "chat_start_time": datetime.datetime.now(),
        "chat_last_time": datetime.datetime.now(),
        "user_id": user_id,
        "title": title or f"对话 {res}"
    }

    return chat["chat_id"]


# 创建消息函数
def create_message(chat_id, text, sender_type, timestamp=None):

    if timestamp is None:
        timestamp = datetime.datetime.now()

    array=['db','messagedb','add_message',text,sender_type,chat_id]
    res=client.send_array_to_server(array)
    
    return res


# 模拟AI回复
def get_ai_response(user_message):
    responses = [
        "我理解您的问题了，让我为您详细解释。",
        "这是一个很好的问题！根据我的知识：",
        "谢谢您的提问！我可以帮您解答这个问题。",
        "让我想想如何最好地回答这个问题...",
        "基于您的问题，我可以提供以下信息："
    ]

    # 简单关键词匹配
    if '你好' in user_message or '嗨' in user_message or 'hello' in user_message:
        return "您好！很高兴为您提供帮助。"
    elif '谢谢' in user_message or '感谢' in user_message:
        return "不客气！如果还有其他问题，请随时问我。"
    elif '机器学习' in user_message:
        return "机器学习是人工智能的核心领域，它使计算机能够在没有明确编程的情况下学习和改进。常见的机器学习类型包括监督学习、无监督学习和强化学习。"
    elif '人工智能' in user_message:
        return "人工智能是计算机科学的一个分支，旨在创建能够执行通常需要人类智能的任务的系统。这些任务包括学习、推理、问题解决、感知和语言理解。"

    return random.choice(responses) + " 您能提供更多细节吗？这样我可以给您更精确的回答。"


# 主页重定向到登录
@app.route('/')
def home():
    return redirect(url_for('login_page'))


# 登录页面
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    # 设置默认值
    default_userid = '123456'
    default_password = '12345678'

    if request.method == 'POST':
        userid = request.form.get('userid')
        password = request.form.get('password')
        remember = request.form.get('remember')

        # 验证逻辑
        if not userid or not password:
            flash('请输入用户名和密码！', 'error')
            return render_template('login.html',
                                   userid=userid if userid else default_userid,
                                   password=password if password else default_password,
                                   remember=remember)

        # 查找用户
        user = None
        array=['db','userdb','check_user_exists',userid]
        res=client.send_array_to_server(array)
        if(res==1):
            array=['db','userdb','get_user_fields',userid,'user_name']
            res=client.send_array_to_server(array)
            redname=res[0]
            array=['db','userdb','get_user_fields',userid,'user_password']
            res=client.send_array_to_server(array)
            redpass=res[0]
            array=['db','userdb','get_user_fields',userid,'user_time']
            res=client.send_array_to_server(array)
            redtime=datetime.datetime.fromisoformat(res[0])
            array=['db','userdb','get_user_fields',userid,'user_interest']
            res=client.send_array_to_server(array)
            redinterest=res[0]
            array=['db','userdb','get_user_fields',userid,'user_strong_interest']
            res=client.send_array_to_server(array)
            redstronginterest=res[0]
            array=['db','userdb','get_user_fields',userid,'user_identity']
            res=client.send_array_to_server(array)
            redidentity=res[0]
            user={
                "user_id": userid,
                "user_name": redname,
                "user_password": redpass.encode('utf-8'),
                "user_time": redtime,
                "user_interest": redinterest,
                "user_strong_interest": redstronginterest,
                "user_identity": redidentity
            }

        if not user:
            flash('用户 '+ userid +' 不存在！', 'error')
            return render_template('login.html',
                                   userid=userid,
                                   password=password,
                                   remember=remember)

        # 验证密码
        if not bcrypt.checkpw(password.encode('utf-8'), user['user_password']):
            flash('密码错误！', 'error')
            return render_template('login.html',
                                   userid=userid,
                                   password=password,
                                   remember=remember)

        # 登录成功
        session['user_id'] = user['user_id']
        session['user_name'] = user['user_name']
        session['user_identity'] = user['user_identity']

        # 查找用户的对话
        array=['db','chatdb','find_chat_by_field',user['user_id']]
        user_chats=client.send_array_to_server(array)
        ##user_chats = [chat for chat in CHATS.values() if chat['user_id'] == user['user_id']]

        # 如果没有对话，创建一个新对话
        if not user_chats:
            # 创建新对话
            array=['db','chatdb','add_chat',user['user_id'],"欢迎对话"]
            new_chat_id = client.send_array_to_server(array)

            # 添加欢迎消息
            array=['db','messagedb','add_message',"您好！我是AI助手，有什么我可以帮助您的吗？",1,new_chat_id]
            res=client.send_array_to_server(array)

            # 设置当前活动对话
            session['active_chat_id'] = new_chat_id
        else:
            # 设置最近的活动对话为当前对话
            user_chats.sort(key=lambda x: x['chat_last_time'], reverse=True)
            session['active_chat_id'] = user_chats[0]['chat_id']

        # 根据身份跳转不同页面
        if user['user_identity'] == '1':  # 管理员
            return redirect(url_for('manager_page'))
        else:  # 普通用户（0）
            return redirect(url_for('chat_page'))

    # GET请求时使用默认值
    return render_template('login.html',
                           userid=default_userid,
                           password=default_password)


# 注册页面
@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        userid = request.form.get('userid')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        username = request.form.get('username')

        # 输入验证
        if not userid:
            flash('用户名不能为空！', 'error')
            return render_template('register.html',
                                   userid=userid,
                                   password=password,
                                   confirm_password=confirm_password,
                                   username=username
                                   )

        if len(userid) < 4 or len(userid) > 20:
            flash('用户名长度需在4-20个字符之间！', 'error')
            return render_template('register.html',
                                   userid=userid,
                                   password=password,
                                   confirm_password=confirm_password,
                                   username=username)

        if not password:
            flash('密码不能为空！', 'error')
            return render_template('register.html',
                                   userid=userid,
                                   password=password,
                                   confirm_password=confirm_password,
                                   username=username)

        if len(password) < 8:
            flash('密码长度至少需要8位！', 'error')
            return render_template('register.html',
                                   userid=userid,
                                   password=password,
                                   confirm_password=confirm_password,
                                   username=username)

        if password != confirm_password:
            flash('两次输入的密码不一致！', 'error')
            return render_template('register.html',
                                   userid=userid,
                                   password=password,
                                   confirm_password=confirm_password,
                                   username=username)

        # 检查用户名是否已存在
        array=['db','userdb','check_user_exists',userid]
        res=client.send_array_to_server(array)
        if(res==1):
            flash('用户名已存在！', 'error')
            return render_template('register.html',
                                    userid=userid,
                                    password=password,
                                    confirm_password=confirm_password,
                                    username=username)


        # 创建新用户
        userid = request.form.get('userid')
        password = request.form.get('password')
        username = request.form.get('username') or userid  # 昵称为空时使用用户名

        # 生成密码哈希
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # 添加到用户表
        array=['db','userdb','add_user',userid,username,password_hash.decode('utf-8')]
        res=client.send_array_to_server(array)
        print(res)

        # 创建初始对话
        chat_id = create_chat(userid)

        # 添加欢迎消息
        create_message(chat_id, "您好！欢迎使用AI助手，有什么我可以帮助您的吗？", 1)  # 系统消息

        flash(f'注册成功！欢迎 {username or userid}！', 'success')
        return redirect(url_for('login_page'))

    # GET请求时返回空表单
    return render_template('register.html')


@app.route('/manager')
def manager_page():
    # 检查是否登录
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    # 检查是否是管理员（假设1表示管理员）
    if session.get('user_identity') != '1':
        flash('需要管理员权限', 'error')
        return redirect(url_for('login_page'))  # 跳转到首页或404

    return render_template('manager.html')


# 加载历史对话
@app.route('/load_chat/<int:chat_id>')
def load_chat(chat_id):
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user_id = session['user_id']

    # 验证对话是否存在且属于当前用户
    array=['db','chatdb','get_chat_fields',chat_id,'all']
    res=client.send_array_to_server(array)
    if (res!=0 and res['user_id']==user_id):
        # 只设置当前活动对话，不更新时间
        session['active_chat_id'] = chat_id

        flash(f'已加载对话: {res["title"]}', 'success')
    else:
        flash('找不到指定的对话！', 'error')

    return redirect(url_for('chat_page'))


# 聊天页面
@app.route('/chat', methods=['GET', 'POST'])
def chat_page():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user_id = session['user_id']
    active_chat_id = session.get('active_chat_id')

    # 获取当前用户信息
    user=None
    array=['db','userdb','check_user_exists',user_id]
    res=client.send_array_to_server(array)
    if(res==1):
        array=['db','userdb','get_user_fields',user_id,'user_name']
        res=client.send_array_to_server(array)
        redname=res[0]
        array=['db','userdb','get_user_fields',user_id,'user_password']
        res=client.send_array_to_server(array)
        redpass=res[0]
        array=['db','userdb','get_user_fields',user_id,'user_time']
        res=client.send_array_to_server(array)
        redtime=datetime.datetime.fromisoformat(res[0])
        array=['db','userdb','get_user_fields',user_id,'user_interest']
        res=client.send_array_to_server(array)
        redinterest=res[0]
        array=['db','userdb','get_user_fields',user_id,'user_strong_interest']
        res=client.send_array_to_server(array)
        redstronginterest=res[0]
        array=['db','userdb','get_user_fields',user_id,'user_identity']
        res=client.send_array_to_server(array)
        redidentity=res[0]
        user={
            "user_id": user_id,
            "user_name": redname,
            "user_password": redpass,
            "user_time": redtime,
            "user_interest": redinterest,
            "user_strong_interest": redstronginterest,
            "user_identity": int(redidentity)
            }
    if not user:
        flash('用户信息错误', 'error')
        return redirect(url_for('login_page'))

    # 处理POST请求（用户发送消息）
    if request.method == 'POST':
        message_text = request.form.get('message')

        if message_text and active_chat_id:
            # 向后端发送聊天请求，让后端调用ChatGLM并处理所有逻辑
            # 命令格式: ['chat', 用户ID, 消息内容, 对话ID]
            array = ['chat', user_id, message_text, active_chat_id]
            response = client.send_array_to_server(array)
            
            # 检查后端返回的数据是否包含错误
            if 'error' in response:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'error': response['error']}), 500
                else:
                    flash(f"服务器错误: {response['error']}", 'error')
                    return redirect(url_for('chat_page'))

            # 如果是AJAX请求，返回JSON响应
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # 后端已经返回了完整的用户和AI消息数据，直接返回即可
                return jsonify({
                    'success': True,
                    'user_message': {
                        'id': response['user_message']['message_id'],
                        'text': response['user_message']['message_text'],
                        'time': datetime.datetime.now().strftime('%H:%M')
                    },
                    'ai_message': {
                        'id': response['ai_message']['message_id'],
                        'text': response['ai_message']['message_text'],
                        'time': datetime.datetime.now().strftime('%H:%M')
                    }
                })
            
            else:
                # 如果不是AJAX请求，重定向到聊天页面
                return redirect(url_for('chat_page'))

        else:
            # 如果消息为空或没有活动对话
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': '消息为空或没有活动对话'}), 400
            flash('消息为空或没有活动对话', 'error')
            return redirect(url_for('chat_page'))

    

    # 获取用户的所有对话
    array=['db','chatdb','find_chat_by_field',user_id]
    user_chats = client.send_array_to_server(array)
    for chat in user_chats:
        chat['chat_last_time']=datetime.datetime.strptime(chat['chat_last_time'].replace("T", " "), "%Y-%m-%d %H:%M:%S.%f")
    

    # 按最后活动时间排序（最新在前）
    user_chats.sort(key=lambda x: x['chat_last_time'], reverse=True)

    # 获取当前对话的消息
    messages = []
    if active_chat_id:
        # 从消息表中获取该对话的所有消息
        array=['db','messagedb','find_message_by_field',str(active_chat_id)]
        messages = client.send_array_to_server(array)
        for msg in messages:
            msg['message_time']=datetime.datetime.strptime(msg['message_time'].replace("T", " "), "%Y-%m-%d %H:%M:%S.%f")
            msg['message_sender_type']=int(msg['message_sender_type'])
        messages.sort(key=lambda x: x['message_time'])  # 按时间顺序排序
    
    # 准备渲染数据
    chat_history = []
    for chat in user_chats:
        # 计算时间标签
        time_label = get_time_label(chat['chat_last_time'])

        chat_history.append({
            "chat_id": chat['chat_id'],
            "title": chat['title'],
            "time_label": time_label
        })

    # 将用户信息传递给模板
    return render_template('chat.html',
                           username=session.get('user_name', '用户'),
                           messages=messages,
                           chat_history=chat_history,
                           active_chat_id=active_chat_id,
                           user=user)  # 添加user变量


@app.route('/new_chat', methods=['POST'])
def new_chat():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user_id = session['user_id']
    title = request.form.get('title', '新对话')

    # 创建新对话
    new_chat_id = create_chat(user_id, title)

    # 添加欢迎消息
    create_message(new_chat_id, "您好！开始新的对话吧，有什么我可以帮助您的吗？", 1)

    # 设置新对话为活动状态
    session['active_chat_id'] = new_chat_id

    flash(f'新对话 "{title}" 已开始！', 'success')
    return redirect(url_for('chat_page'))


# 登出功能
@app.route('/logout')
def logout():
    session.pop('userid', None)
    session.pop('username', None)
    flash('您已成功登出！', 'success')
    return redirect(url_for('login_page'))


@app.route('/delete_chat/<int:chat_id>', methods=['POST', 'GET', 'DELETE'])
def delete_chat(chat_id):
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user_id = session['user_id']

    # 验证对话是否存在
    array=['db','chatdb','get_chat_fields',chat_id,'all']
    res=client.send_array_to_server(array)
    if (res!=0):
        # 删除对话
        array=['db','chatdb','delete_chat',chat_id]
        res=client.send_array_to_server(array)

        # 删除相关消息
        array=['db','messagedb','delete_message_by_chat_id',chat_id]
        res=client.send_array_to_server(array)

        # 清除活动对话
        if session.get('active_chat_id') == chat_id:
            session.pop('active_chat_id', None)

        flash('对话已删除', 'success')
    else:
        flash('找不到指定的对话！', 'error')

    return redirect(url_for('chat_page'))


# 更新个人信息路由
@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '用户未登录'})

    user_id = session['user_id']
    data = request.get_json()
    new_username = data.get('username')

    if not new_username:
        return jsonify({'success': False, 'message': '昵称不能为空'})

    # 更新用户昵称
    array=['db','userdb','update_user_field',user_id,'user_name',new_username]
    res=client.send_array_to_server(array)
    session['username'] = new_username
    return jsonify({'success': True, 'message': '昵称更新成功'})

    ##return jsonify({'success': False, 'message': '用户不存在'})


# 更新密码路由
@app.route('/update_password', methods=['POST'])
def update_password():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '用户未登录'})

    user_id = session['user_id']
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not current_password or not new_password:
        return jsonify({'success': False, 'message': '请提供所有密码字段'})
    
    array=['db','userdb','check_user_exists',user_id]
    res=client.send_array_to_server(array)
    if (res==1):
        # 验证当前密码
        array=['db','userdb','get_user_fields',123456,'user_password']
        res=client.send_array_to_server(array)
        if not bcrypt.checkpw(current_password.encode('utf-8'), res[0].encode('utf-8')):
            return jsonify({'success': False, 'message': '当前密码不正确'})

        # 更新密码
        new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        array=['db','userdb','update_user_field',user_id,'user_password',new_password_hash.decode('utf-8')]
        res=client.send_array_to_server(array)
        return jsonify({'success': True, 'message': '密码更新成功'})

    return jsonify({'success': False, 'message': '用户不存在'})

# 用户管理页面路由
@app.route('/manage_user')
def manage_user_page():
    # 检查是否登录
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user_id = session['user_id']

    # 检查当前用户是否是管理员
    if session.get('user_identity') != '1':
        flash('需要管理员权限', 'error')
        return redirect(url_for('chat_page'))

    # 获取所有用户数据（不包含密码）
    safe_users = {}
    array=['db','userdb','get_all_users']
    res=client.send_array_to_server(array)
    for user in res:
        user['user_identity']=int(user['user_identity'])
        safe_user = user.copy()
        safe_user.pop('user_password', None)  # 移除密码字段
        uid=user['user_id']
        safe_users[uid] = safe_user

    return render_template('manage_user.html', users=safe_users)


# 确保所有 API 路由返回 JSON 响应
@app.route('/api/users')
def get_users():
    # 检查是否登录
    if 'user_id' not in session:
        return jsonify({'error': '未登录'}), 401

    user_id = session['user_id']

    # 检查当前用户是否是管理员
    if session.get('user_identity') != '1':
        return jsonify({'error': '无权限'}), 403

    # 创建不包含密码的用户数据副本
    safe_users = {}
    array=['db','userdb','get_all_users']
    res=client.send_array_to_server(array)
    for user in res:
        user['user_identity']=int(user['user_identity'])
        safe_user = user.copy() 
        safe_user.pop('user_password', None)  # 移除密码字段
        uid=user['user_id']
        safe_users[uid] = safe_user

    return jsonify(safe_users)


@app.route('/api/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    # 检查是否登录
    if 'user_id' not in session:
        return jsonify({'error': '未登录'}), 401

    current_user_id = session['user_id']

    # 检查当前用户是否是管理员
    if session.get('user_identity') != '1':
        return jsonify({'error': '无权限'}), 403

    # 检查目标用户是否存在
    array=['db','userdb','check_user_exists',user_id]
    res=client.send_array_to_server(array)
    if (res==0):
        return jsonify({'error': '用户不存在'}), 404

    data = request.get_json()
    array=['db','userdb','update_user_field',user_id,'user_name',data['username']]
    res=client.send_array_to_server(array)
    if current_user_id == user_id:
        session['user_name'] = data['username']

    return jsonify({'success': True, 'message': '用户信息已更新'})


@app.route('/api/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    # 检查是否登录
    if 'user_id' not in session:
        return jsonify({'error': '未登录'}), 401

    current_user_id = session['user_id']

    # 检查当前用户是否是管理员
    if session.get('user_identity') != '1':
        return jsonify({'error': '无权限'}), 403

    # 检查目标用户是否存在
    array=['db','userdb','check_user_exists',user_id]
    res=client.send_array_to_server(array)
    if (res==0):
        return jsonify({'error': '用户不存在'}), 404

    # 检查是否尝试删除管理员账号
    array=['db','userdb','get_user_fields',user_id,'user_identity']
    res=client.send_array_to_server(array)
    if res == '1':
        # 管理员只能删除自己（注销账号）
        if user_id != current_user_id:
            return jsonify({'error': '不能删除其他管理员账号'}), 403

    try:
        # 删除用户
        array=['db','userdb','delete_user_by_id',user_id]
        res=client.send_array_to_server(array)

        # 如果删除的是当前用户自己，登出
        if user_id == current_user_id:
            session.clear()
            return jsonify({
                'success': True,
                'message': '账号已注销',
                'redirect': url_for('login_page')
            })

        return jsonify({'success': True, 'message': '用户已删除'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 全局错误处理
@app.errorhandler(404)
def page_not_found(error):
    return jsonify({'error': '资源未找到'}), 404


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'error': '服务器内部错误'}), 500


# 确保所有路由返回 JSON 响应
@app.after_request
def set_response_type(response):
    # 只处理 API 路由
    if request.path.startswith('/api/'):
        response.headers['Content-Type'] = 'application/json'
    return response


# 确认管理员授权API
@app.route('/api/users/<user_id>/confirm_promotion', methods=['POST'])
def confirm_promotion(user_id):
    # 检查是否登录
    if 'user_id' not in session:
        return jsonify({'error': '未登录'}), 401

    current_user_id = session['user_id']

    # 检查当前用户是否是管理员
    if session.get('user_identity') != '1':
        return jsonify({'error': '无权限'}), 403

    # 检查目标用户是否存在
    array=['db','userdb','check_user_exists',user_id]
    res=client.send_array_to_server(array)
    if (res==0):
        return jsonify({'error': '用户不存在'}), 404

    # 提升用户为管理员
    array=['db','userdb','update_user_field',user_id,'user_identity',1]
    res=client.send_array_to_server(array)

    return jsonify({'success': True, 'message': '用户已提升为管理员'})

@app.route('/manage_chat')
def manage_chat():
    # 检查是否登录且是管理员
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    if session.get('user_identity') != '1':
        flash('您没有访问此页面的权限', 'error')
        return redirect(url_for('chat_page'))

    # 获取搜索参数
    search_term = request.args.get('search', '')

    # 获取选中的对话ID
    active_chat_id = request.args.get('chat_id', type=int)
    active_chat = None
    messages = []

    # 准备对话数据
    conversations = []
    array=['db','chatdb','get_all_chats']
    res=client.send_array_to_server(array)
    for chat in res:
        chat['chat_start_time']=datetime.datetime.strptime(chat['chat_start_time'].replace("T", " "), "%Y-%m-%d %H:%M:%S.%f")
        chat['chat_last_time']=datetime.datetime.strptime(chat['chat_last_time'].replace("T", " "), "%Y-%m-%d %H:%M:%S.%f")
    for chat in res:
        chat_id=int(chat['chat_id'])
        # 获取对话所属用户的信息
        array=['db','userdb','get_user_fields',chat['user_id'],'all']
        user = client.send_array_to_server(array)
        """if 'user_id' in user and isinstance(user['user_id'], str) and user['user_id'].isdigit():
            user['user_id'] = int(user['user_id'])"""
        if not user:
            continue

        # 计算时间标签
        time_label = get_time_label(chat['chat_last_time'])

        # 如果没有搜索词，或者对话符合搜索条件
        if not search_term or (
                search_term.lower() in chat['title'].lower() or
                search_term.lower() in user['user_name'].lower() or
                search_term == str(user['user_id'])
        ):
            conversations.append({
                'chat_id': chat_id,
                'user_id': user['user_id'],
                'user_name': user['user_name'],
                'title': chat['title'],
                'create_time': chat['chat_start_time'],
                'last_time': chat['chat_last_time'],
                'time_label': time_label
            })

        # 如果是选中的对话
        if chat_id == active_chat_id:
            active_chat = {
                'chat_id': chat_id,
                'user_id': user['user_id'],
                'user_name': user['user_name'],
                'title': chat['title'],
                'create_time': chat['chat_start_time'],
                'last_time': chat['chat_last_time']
            }

    # 按最后活动时间排序（最新在前）
    conversations.sort(key=lambda x: x['last_time'], reverse=True)

    # 获取选中对话的消息
    if active_chat_id:
        # 从消息表中获取该对话的所有消息
        array=['db','messagedb','find_message_by_field',str(active_chat_id)]
        messages = client.send_array_to_server(array)
        for msg in messages:
            msg['message_time']=datetime.datetime.strptime(msg['message_time'].replace("T", " "), "%Y-%m-%d %H:%M:%S.%f")
            msg['message_sender_type']=int(msg['message_sender_type'])
        messages.sort(key=lambda x: x['message_time'])  # 按时间顺序排序
        print(messages)

    return render_template('manage_chat.html',
                           username=session.get('user_name', '管理员'),
                           conversations=conversations,
                           active_chat=active_chat,
                           active_chat_id=active_chat_id,
                           messages=messages,
                           search_term=search_term)

# 情感词管理页面路由
@app.route('/emoword')
def manage_emoword_page():
    # 检查是否登录
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user_id = session['user_id']

    # 检查当前用户是否是管理员
    if session.get('user_identity') != '1':
        flash('需要管理员权限', 'error')
        return redirect(url_for('chat_page'))

    # 获取所有情感词数据
    emowords_list = []
    array=['db','emworddb','get_all_senword']
    res=client.send_array_to_server(array)
    for emoword_data in res:
        emowords_list.append({
            'emoword_id': int(emoword_data[0]['emword_id']),
            'emoword_text': emoword_data[0]['emword_text'],
            'emoword_sentiment': emoword_data[0]['emword_sentiment'],
            'emoword_sen_height': int(emoword_data[0]['emword_sen_height'])
        })

    # 按ID排序
    emowords_list.sort(key=lambda x: x['emoword_id'])

    return render_template('emoword.html', emowords=emowords_list)


# 情感词API路由 - 返回所有情感词数据
@app.route('/api/emowords')
def get_emowords():
    # 检查是否登录
    if 'user_id' not in session:
        return jsonify({'error': '未登录'}), 401

    user_id = session['user_id']

    # 检查当前用户是否是管理员
    if session.get('user_identity') != '1':
        return jsonify({'error': '无权限'}), 403

    # 创建情感词数据列表
    emowords_list = []
    array=['db','emworddb','get_all_senword']
    res=client.send_array_to_server(array)
    for emoword_data in res:
        emowords_list.append({
            'emoword_id': int(emoword_data[0]['emword_id']),
            'emoword_text': emoword_data[0]['emword_text'],
            'emoword_sentiment': emoword_data[0]['emword_sentiment'],
            'emoword_sen_height': int(emoword_data[0]['emword_sen_height'])
        })

    # 按ID排序
    emowords_list.sort(key=lambda x: x['emoword_id'])

    return jsonify(emowords_list)


# 添加情感词API
@app.route('/api/emowords/add', methods=['POST'])
def add_emoword():
    # 验证管理员权限
    if session.get('user_identity') != '1':
        return jsonify({'error': '权限不足'}), 403

    data = request.json
    text = data.get('text', '').strip()
    sentiment = data.get('sentiment', '')
    sen_height = data.get('sen_height', 0)

    # 验证输入
    if not text:
        return jsonify({'error': '情感词不能为空'}), 400

    valid_sentiments = ['高兴', '悲伤', '愤怒', '恐惧', '惊讶', '厌恶', '中性', '期待']
    if sentiment not in valid_sentiments:
        return jsonify({'error': '无效的情感类型'}), 400

    if not isinstance(sen_height, int) or sen_height < 1 or sen_height > 10:
        return jsonify({'error': '情感强度必须在1-10之间'}), 400

    # 检查情感词是否已存在
    array=['db','emworddb','check_emword_by_field',text]
    res=client.send_array_to_server(array)
    if (res==1):
        return jsonify({'error': '情感词已存在'}), 400


    # 添加新情感词
    array=['db','emworddb','add_emword',text,sentiment,sen_height]
    res=client.send_array_to_server(array)
    newword = {
        'emoword_id': res,
        'emoword_text': text,
        'emoword_sentiment': sentiment,
        'emoword_sen_height': sen_height
    }

    return jsonify({
        'success': True,
        'message': '情感词添加成功',
        'emoword': newword
    })


# 更新情感词API
@app.route('/api/emowords/<int:emoword_id>', methods=['PUT'])
def update_emoword(emoword_id):
    # 验证管理员权限
    if session.get('user_identity') != '1':
        return jsonify({'error': '权限不足'}), 403

    data = request.json
    text = data.get('text', '').strip()
    sentiment = data.get('sentiment', '')
    sen_height = data.get('sen_height', 0)

    # 验证输入
    if not text:
        return jsonify({'error': '情感词不能为空'}), 400

    valid_sentiments = ['高兴', '悲伤', '愤怒', '恐惧', '惊讶', '厌恶', '中性', '期待']
    if sentiment not in valid_sentiments:
        return jsonify({'error': '无效的情感类型'}), 400

    if not isinstance(sen_height, int) or sen_height < 1 or sen_height > 10:
        return jsonify({'error': '情感强度必须在1-10之间'}), 400

    # 更新情感词
    array=['db','emworddb','update_emword_field',emoword_id,'emword_text',text]
    res=client.send_array_to_server(array)
    array=['db','emworddb','update_emword_field',emoword_id,'emword_sentiment',sentiment]
    res=client.send_array_to_server(array)
    array=['db','emworddb','update_emword_field',emoword_id,'emword_sen_height',sen_height]
    res=client.send_array_to_server(array)
    newemword = {
        'emoword_id': emoword_id,
        'emoword_text': text,
        'emoword_sentiment': sentiment,
        'emoword_sen_height': sen_height
    }

    return jsonify({
        'success': True,
        'message': '情感词更新成功',
        'emoword': newemword
    })


# 删除情感词API
@app.route('/api/emowords/<int:emoword_id>', methods=['DELETE'])
def delete_emoword(emoword_id):
    # 验证管理员权限
    if session.get('user_identity') != '1':
        return jsonify({'error': '权限不足'}), 403

    # 从内存存储中删除
    array=['db','emworddb','delete_emword',emoword_id]
    res=client.send_array_to_server(array)


    return jsonify({
        'success': True,
        'message': '情感词删除成功',
        'deleted_emoword': emoword_id
    })


# 搜索情感词API
@app.route('/api/emowords/search', methods=['GET'])
def search_emowords():
    # 验证管理员权限
    if session.get('user_identity') != '1':
        return jsonify({'error': '权限不足'}), 403

    search_term = request.args.get('term', '').strip().lower()

    if not search_term:
        return jsonify({'error': '搜索词不能为空'}), 400

    # 在内存存储中搜索
    results = []
    array=['db','emworddb','get_all_senword']
    res=client.send_array_to_server(array)
    for emoword_data in res:
        if (search_term in emoword_data[0]['emword_text'].lower() or
                search_term in emoword_data[0]['emword_sentiment'].lower()):
            results.append({
                'emoword_id': int(emoword_data[0]['emword_id']),
                'emoword_text': emoword_data[0]['emword_text'],
                'emoword_sentiment': emoword_data[0]['emword_sentiment'],
                'emoword_sen_height': int(emoword_data[0]['emword_sen_height'])
            })

    # 按ID排序
    results.sort(key=lambda x: x['emoword_id'])
    return jsonify(results)


# 获取情感类型选项API
@app.route('/api/emowords/sentiment_options', methods=['GET'])
def get_sentiment_options():
    # 返回8种情绪分类作为选项
    valid_sentiments = ['高兴', '悲伤', '愤怒', '恐惧', '惊讶', '厌恶', '中性', '期待']
    return jsonify(valid_sentiments)


# 敏感词管理页面路由
@app.route('/senword')
def manage_senword_page():
    # 检查是否登录
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user_id = session['user_id']

    # 检查当前用户是否是管理员
    if session.get('user_identity') != '1':
        flash('需要管理员权限', 'error')
        return redirect(url_for('chat_page'))

    # 获取所有敏感词数据
    senwords_list = []
    array=['db','senworddb','get_all_senword']
    res=client.send_array_to_server(array)
    for senword_data in res:
        senwords_list.append({
            'senword_id': int(senword_data[0]),
            'senword_text': senword_data[1][0]
        })

    # 按ID排序
    senwords_list.sort(key=lambda x: x['senword_id'])

    return render_template('senword.html', senwords=senwords_list)



@app.route('/api/senwords', methods=['GET'])
def get_senwords():
    # 检查管理员权限
    if session.get('user_identity') != '1':
        return jsonify({"error": "权限不足"}), 403

    # 返回所有敏感词
    senwords_list = []
    array=['db','senworddb','get_all_senword']
    res=client.send_array_to_server(array)
    for senword_data in res:
        senwords_list.append({
            'senword_id': int(senword_data[0]),
            'senword_text': senword_data[1][0]
        })

    # 按ID排序
    senwords_list.sort(key=lambda x: x['senword_id'])
    return jsonify(senwords_list)


@app.route('/api/senwords/add', methods=['POST'])
def add_senword():
    # 检查管理员权限
    if session.get('user_identity') != '1':
        return jsonify({"error": "权限不足"}), 403

    data = request.json
    text = data.get('text', '').strip()

    # 验证输入
    if not text:
        return jsonify({"error": "敏感词不能为空"}), 400

    # 添加新敏感词
    array=['db','senworddb','add_senword',text]
    res=client.send_array_to_server(array)
    new_senword = {
        "senword_id": res,
        "senword_text": text
    }

    return jsonify({
        "success": True,
        "message": "敏感词添加成功",
        "senword": new_senword
    })


@app.route('/api/senwords/<int:senword_id>', methods=['DELETE'])
def delete_senword(senword_id):
    # 检查管理员权限
    if session.get('user_identity') != '1':
        return jsonify({"error": "权限不足"}), 403

    # 删除敏感词
    array=['db','senworddb','delete_senword',senword_id]
    res=client.send_array_to_server(array)

    return jsonify({
        "success": True,
        "message": "敏感词删除成功",
        "deleted_senword": senword_id
    })


@app.route('/api/senwords/search', methods=['GET'])
def search_senwords():
    # 检查管理员权限
    if session.get('user_identity') != '1':
        return jsonify({"error": "权限不足"}), 403

    search_term = request.args.get('term', '').strip().lower()

    if not search_term:
        return jsonify({"error": "搜索词不能为空"}), 400

    # 搜索敏感词
    results = []
    array=['db','senworddb','get_all_senword']
    res=client.send_array_to_server(array)
    for senword in res:
        senword[0]=int(senword[0])
        if search_term in senword[1][0].lower():
            new_senword = {
                "senword_id": senword[0],
                "senword_text": search_term
            }
            results.append(new_senword)

    return jsonify(results)

@app.route('/update_interests', methods=['POST'])
def update_interests():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '用户未登录'}), 401

    user_id = session['user_id']
    data = request.get_json()

    # 更新用户兴趣
    array=['db','userdb','update_user_field',user_id,'user_interest',json.dumps(data['interests'])]
    res=client.send_array_to_server(array)
    array=['db','userdb','update_user_field',user_id,'user_strong_interest',json.dumps(data['strong_interests'])]
    res=client.send_array_to_server(array)

    return jsonify({'success': True})


# 添加自定义Jinja2过滤器
@app.template_filter('from_json')
def json_loads_filter(value):
    """将JSON字符串解析为Python对象"""
    try:
        return json.loads(value) if value else []
    except (TypeError, json.JSONDecodeError):
        return []

if __name__ == '__main__':
    app.run(debug=True)