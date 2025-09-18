from datetime import datetime, timedelta
import json
import time
import redisdb

    
def clear_all_chat():
    """
    清空所有记录数据
    """
    redis_client = redisdb.get_redis_connection()
    chat_keys = redis_client.keys("chat:*")
    if not chat_keys:
        return 0
    redis_client.delete("id:counter:chat")
    return redis_client.delete(*chat_keys)

def get_next_id_with_init(redis_client,counter_key="id:counter:chat", initial_id=1):
    """
    获取下一个自增ID（带初始化）
    """
    # 如果计数器不存在，设置初始值并返回
    if not redis_client.exists(counter_key):
        redis_client.set(counter_key, initial_id)
        return initial_id
    
    # 如果计数器已存在，递增并返回
    next_id = redis_client.incr(counter_key)
    return next_id

def check_chat_exists(redis_client,chat_id):
    """
    检查是否存在
    """
    chat_key = f"chat:{chat_id}"
    exists = redis_client.exists(chat_key)
    if(bool(exists==True)):
        return 1
    else:
        return 0
    
def add_chat(user_id,title):
    redis_client=redisdb.get_redis_connection()
    chat_id =get_next_id_with_init(redis_client)
    timestamp = datetime.now()
    chat_data={
        'chat_id': chat_id,
        'chat_start_time': timestamp.isoformat(),
        'chat_last_time': timestamp.isoformat(),
        'user_id': user_id,
        'title': title
    }
    pipe=redis_client.pipeline()
    pipe.hset(f"chat:{chat_id}", mapping=chat_data)
    results = pipe.execute()
    return chat_id

def delete_chat(chat_id):
    redis_client=redisdb.get_redis_connection()
    if(check_chat_exists(redis_client,chat_id)==0):
        return False
    chat_key = f"chat:{chat_id}"
    results = redis_client.delete(chat_key)
    if(bool(results==True)):
        return 1
    else:
        return 0

def get_chat_fields(chat_id, fields):
    """
    获取特定字段的信息
    """
    redis_client=redisdb.get_redis_connection()

    chat_key = f"chat:{chat_id}"
    if(check_chat_exists(redis_client,chat_id)==0):
        return False
    if (fields =='all'):
        # 获取所有字段
        return redis_client.hgetall(chat_key)
    else:
        # 获取指定字段
        if isinstance(fields, str):
            fields = [fields]
        return redis_client.hmget(chat_key, fields)
    
def update_chat_field(chat_id, field_name, field_value):
    """
    更新特定字段
    """

    redis_client = redisdb.get_redis_connection()
    chat_key = f"chat:{chat_id}"
    
    # 检查用户是否存在
    if(check_chat_exists(redis_client,chat_id)==0):
        return 0
    
    # 更新字段
    results = redis_client.hset(chat_key, field_name, field_value)
    if(bool(results)==True):
        return 1
    else:
        return 0

def find_chat_by_field(field_value, field_name='user_id', limit=8):
    """
    根据字段值查找，返回最近的几条记录（包含全部字段）
    """
    redis_client = redisdb.get_redis_connection()
    records = []
    
    chat_keys = redis_client.keys("chat:*")
    
    for chat_key in chat_keys:
        # 获取字段值
        value = redis_client.hget(chat_key, field_name)
        if value == field_value:
            record_id = int(chat_key.split(':')[1])
            # 获取所有字段
            record_data = redis_client.hgetall(chat_key)
            records.append((record_id, record_data))
    
    # 按记录ID降序排序（ID越大越新）
    records.sort(key=lambda x: x[0], reverse=True)
    
    # 返回最近的几条记录的完整数据
    return [record_data for record_id, record_data in records[:limit]]

def get_all_chats():
    """
    获取所有用户信息（使用 SCAN 安全迭代）
    """
    redis_client = redisdb.get_redis_connection()
    chats = []
    cursor = 0
    pattern = "chat:*"
    
    try:
        while True:
            cursor, keys = redis_client.scan(cursor=cursor, match=pattern, count=100)
            
            # 批量获取所有用户数据
            if keys:
                pipe = redis_client.pipeline()
                for key in keys:
                    pipe.hgetall(key)
                chat_data_list = pipe.execute()
                
                # 处理用户数据
                for key, chat_data in zip(keys, chat_data_list):
                    if chat_data:
                        chats.append(chat_data)
            
            # 迭代完成
            if cursor == 0:
                break
                
    except Exception as e:
        print(f"获取用户列表时出错: {e}")
    
    return chats

def test():
    clear_all_chat()
    print("用户123")
    result=find_chat_by_field('123')
    print(result)
    print("用户111")
    result=find_chat_by_field('111')
    print(result)
    print("添加聊天测试")
    add_chat(123,'交互')
    add_chat(123,'识别')
    add_chat(111,'你好')
    print("用户123")
    result=find_chat_by_field('123')
    print(result)
    print("用户111")
    result=find_chat_by_field('111')
    print(result)
    print("读取聊天信息测试")
    result=get_chat_fields(1,'all')
    print(result)
    result=get_chat_fields(1,'chat_last_time')
    print(result)
    print("更新聊天测试")
    timestamp = datetime.now()
    update_chat_field(1,'chat_last_time',timestamp.isoformat())
    result=get_chat_fields(1,'chat_last_time')
    print(result)
    print("删除聊天测试")
    result=delete_chat(1)
    print("用户123")
    result=find_chat_by_field('123')
    print(result)
    print("用户111")
    result=find_chat_by_field('111')
    print(result)
    clear_all_chat()

    
if __name__ == "__main__":
    test()