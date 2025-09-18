import os
import sys
import socket
import threading
import json
import time
import requests




# 导入数据库相关模块
import redisdb
import chatdb
import messagedb
import db_dispatch
import userdb
import datetime

# ==============================
# 设置环境变量，屏蔽 transformers 编译信息
# ==============================
os.environ["TRANSFORMERS_NO_COMPILATION"] = "1"
# 可选：屏蔽所有 stderr 输出（注意：所有报错信息都会被屏蔽）
# sys.stderr = open(os.devnull, "w")


# 全局变量，用于存储模型和分词器，只加载一次
global_tokenizer = None
global_model = None


# ==============================
# 加载 tokenizer 和模型
# ==============================
from transformers import AutoTokenizer, AutoModel


def load_chatglm_model():
    """在服务器启动时加载模型和分词器"""
    global global_tokenizer, global_model
    print("==== 正在加载 ChatGLM 模型... ====")
    try:
        model_path = "D:\\data\\llm\\chatglm-6b-int4"
        global_tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        global_model = AutoModel.from_pretrained(model_path, trust_remote_code=True).half().cuda()
        global_model = global_model.eval()
        print("==== 模型加载完成 ====")
        return True
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        return False


#===============================
#加载情感分析模块
#===============================
# 导入情感分析模型类
"""from emotion_classifier import EnhancedPaddleEmotionClassifier
global_emotion_classifier = None
def load_emotion_classifier():
    global global_emotion_classifier
    print("==== 正在加载 情感分析 模型... ====")
    try:
        global_emotion_classifier = EnhancedPaddleEmotionClassifier()
        print("✅ 情感分析模型初始化成功。")
        return True
    except Exception as e:
        print(f"❌ 情感分析模型初始化失败: {e}")
        return False
"""

# ==============================
# 聊天处理函数
# ==============================
def handle_chat_request(user_id, user_message, chat_id):
    """
    处理聊天请求，先检查敏感词，然后调用ChatGLM模型，并保存聊天记录到数据库。
    """
    print(f"处理用户 {user_id} 的聊天请求: {user_message}")

    try:
        # 1. 敏感词检查
        sensitive_words_data = db_dispatch.dispatch(['senworddb', 'get_all_senword'])
        print(f"敏感词数据: {sensitive_words_data}")
        
        # 关键修复：检查返回的数据类型，如果不是列表则跳过，防止TypeError
        if sensitive_words_data and isinstance(sensitive_words_data, list):
            # 修正：从数据库返回的列表中提取敏感词字符串，而不是整个列表
            sensitive_words = [item[1][0] for item in sensitive_words_data]
            is_sensitive = False
            for senword in sensitive_words:
                if senword in user_message:
                    is_sensitive = True
                    print(f"检测到敏感词: {senword}")
                    break
        else:
            is_sensitive = False

        # 如果检测到敏感词，直接返回固定回复
        if is_sensitive:
            ai_response = "您的话中含有敏感词，请换个话题吧"
            
            user_message_id = db_dispatch.dispatch(['messagedb', 'add_message', user_message, 0, chat_id])
            ai_message_id = db_dispatch.dispatch(['messagedb', 'add_message', ai_response, 1, chat_id])

            db_dispatch.dispatch(['chatdb', 'update_chat_field', chat_id, 'chat_last_time', datetime.datetime.now().isoformat()])
            
            user_message_data = db_dispatch.dispatch(['messagedb', 'get_message_fields', user_message_id, 'all'])
            ai_message_data = db_dispatch.dispatch(['messagedb', 'get_message_fields', ai_message_id, 'all'])

            return {
                'user_message': user_message_data,
                'ai_message': ai_message_data
            }
        
        # 2. 情感分析与个性化提示
        modified_user_message = user_message
        try:
            # 向独立的情感分析服务发送请求
            emotion_service_url = 'http://127.0.0.1:5001/predict_emotion'
            response = requests.post(emotion_service_url, json={'text': user_message}, timeout=3)
            
            if response.status_code == 200:
                emotion_result = response.json()
                emotion = emotion_result['emotion']
                emotion_prompt = f"请根据以下用户的情感状态，以相应的情绪和语气进行回复。用户情感：{emotion}。"
                modified_user_message = emotion_prompt + " " + user_message
                print(f"用户情感分析结果: {emotion}，已将输入修改为：'{modified_user_message}'")
            else:
                print(f"❌ 情感分析服务返回错误: {response.status_code}, {response.text}")
                print("将使用原始消息。")
        except requests.exceptions.RequestException as e:
            print(f"❌ 无法连接到情感分析服务: {e}")
            print("将使用原始消息。")
        except Exception as e:
            print(f"情感分析失败: {e}，将使用原始消息。")


        """
        modified_user_message = user_message
        if 'global_emotion_classifier' in globals() and global_emotion_classifier:
            try:
                emotion_result = global_emotion_classifier.predict_emotion(user_message)
                emotion = emotion_result['emotion']
                # 构造包含情感信息的提示语，作为ChatGLM的额外输入
                emotion_prompt = f"请根据以下用户的情感状态，以相应的情绪和语气进行回复。用户情感：{emotion}。"
                modified_user_message = emotion_prompt + " " + user_message
                print(f"用户情感分析结果: {emotion}，已将输入修改为：'{modified_user_message}'")
            except Exception as e:
                print(f"情感分析失败: {e}，将使用原始消息。")
        """

        # 3. 如果没有敏感词，继续执行原有的聊天逻辑
        message_history = messagedb.find_message_by_field(chat_id, 'chat_id', limit=10)
        message_history.reverse()

        history = []
        if message_history:
            for msg in message_history:
                if msg['message_sender_type'] == '0':
                    history.append((msg['message_text'], ""))
                else:
                    if history:
                        last_user_msg = history[-1]
                        history[-1] = (last_user_msg[0], msg['message_text'])

        print("正在调用 ChatGLM 模型...")
        response, history_updated = global_model.chat(global_tokenizer, user_message, history=history)
        print(f"ChatGLM: {response}")

        user_message_id = db_dispatch.dispatch(['messagedb', 'add_message', user_message, 0, chat_id])
        ai_message_id = db_dispatch.dispatch(['messagedb', 'add_message', response, 1, chat_id])

        db_dispatch.dispatch(['chatdb', 'update_chat_field', chat_id, 'chat_last_time', datetime.datetime.now().isoformat()])

        user_message_data = db_dispatch.dispatch(['messagedb', 'get_message_fields', user_message_id, 'all'])
        ai_message_data = db_dispatch.dispatch(['messagedb', 'get_message_fields', ai_message_id, 'all'])

        return {
            'user_message': user_message_data,
            'ai_message': ai_message_data
        }

    except Exception as e:
        print(f"处理聊天请求时发生错误: {e}")
        return {'error': f"服务器处理错误: {e}"}



# ==============================
# 服务器逻辑
# ==============================
import userdb
# ...其他导入保持不变...

def handle_client(conn, addr):
    """
    处理一个单独的客户端连接
    """
    print(f"[新连接] {addr} 已连接。")
    conn.setblocking(True)

    while True:
        try:
            data = conn.recv(4096)
            if not data:
                print(f"[连接关闭] {addr} 断开了连接。")
                break

            try:
                received_array = json.loads(data.decode('utf-8'))
                print(f"[来自 {addr}] 接收到数组：{received_array}")

                if not isinstance(received_array, list):
                    error_msg = json.dumps({"error": "请发送一个有效的数组"})
                    conn.send(error_msg.encode('utf-8'))
                    continue

                command_type = received_array[0]
                response_data = {}

                # 根据命令类型分发处理
                if command_type == 'db':
                    del received_array[0]
                    # 直接调用 db_dispatch 函数，它会处理所有的数据库请求
                    response_data = db_dispatch.dispatch(received_array)
                elif command_type == 'chat':
                    if len(received_array) >= 3:
                        user_id = received_array[1]
                        user_message = received_array[2]
                        chat_id = received_array[3] if len(received_array) > 3 else None
                        response_data = handle_chat_request(user_id, user_message, chat_id)
                    else:
                        response_data = {'error': "聊天命令需要至少3个参数：['chat', '用户ID', '消息内容']"}
                else:
                    response_data = {'error': "未知命令类型"}
                
                # 确保返回的是JSON格式，并且支持中文
                response_msg = json.dumps(response_data, ensure_ascii=False)
                conn.send(response_msg.encode('utf-8'))

            except json.JSONDecodeError:
                error_msg = json.dumps({"error": "无效的JSON数据"})
                conn.send(error_msg.encode('utf-8'))
            except Exception as e:
                error_msg = json.dumps({"error": f"服务器处理错误: {e}"})
                conn.send(error_msg.encode('utf-8'))

        except ConnectionResetError:
            print(f"[连接异常] {addr} 连接被重置。")
            break
        except Exception as e:
            print(f"[处理 {addr} 时发生错误]： {e}")
            break

    conn.close()

def start_server(host='127.0.0.1', port=12345):
    """启动服务器"""
    if not load_chatglm_model():
        print("服务器启动失败，请检查glm模型文件路径。")
        return
    

    # 确保成功加载情感分析模型
    """
    if not load_emotion_classifier():
        print("服务器启动失败，请检查情感分析模型文件路径。")
        return
    """

    redis_conn = redisdb.get_redis_connection()
    if not redis_conn:
        print("服务器启动失败，无法连接到Redis。")
        return

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"[服务器启动] 监听于 {host}:{port} ...")
        print("[服务器就绪] 等待接收客户端发送的数组...")

        while True:
            conn, addr = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.daemon = True
            thread.start()

    except Exception as e:
        print(f"[服务器错误]： {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()