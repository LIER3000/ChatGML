from datetime import datetime, timedelta
import json
import time
import redisdb

def clear_all_message():
    """
    清空所有记录数据
    """
    redis_client = redisdb.get_redis_connection()
    message_keys = redis_client.keys("message:*")
    if not message_keys:
        return 0
    redis_client.delete("id:counter:message")
    return redis_client.delete(*message_keys)

def get_next_id_with_init(redis_client,counter_key="id:counter:message", initial_id=1):
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

def check_message_exists(redis_client,message_id):
    """
    检查是否存在
    """
    message_key = f"message:{message_id}"
    exists = redis_client.exists(message_key)
    if(bool(exists)==True):
        return 1
    else:
        return 0 

def add_message(message_text,message_sender_type,chat_id):
    redis_client = redisdb.get_redis_connection()
    message_id = get_next_id_with_init(redis_client)
    timestamp = datetime.now()
    message_data={
        'message_id': message_id,
        'message_text': message_text,
        'message_time': timestamp.isoformat(),
        'message_sender_type': message_sender_type,
        'chat_id': chat_id
    }
    pipe=redis_client.pipeline()
    pipe.hset(f"message:{message_id}", mapping=message_data)
    results = pipe.execute()
    return message_id

def delete_message(message_id):
    redis_client=redisdb.get_redis_connection()
    if(check_message_exists(redis_client,message_id)==0):
        return False
    message_key = f"message:{message_id}"
    results = redis_client.delete(message_key)
    if(bool(results)==True):
        return 1
    else:
        return 0

def get_message_fields(message_id, fields):
    """
    获取特定字段的信息
    """
    redis_client=redisdb.get_redis_connection()

    message_key = f"message:{message_id}"
    if(check_message_exists(redis_client,message_id)==0):
        return False
    if (fields=='all'):
        # 获取所有字段
        return redis_client.hgetall(message_key)
    else:
        # 获取指定字段
        if isinstance(fields, str):
            fields = [fields]
        return redis_client.hmget(message_key, fields)
    
def update_message_field(message_id, field_name, field_value):
    """
    更新特定字段
    """

    redis_client = redisdb.get_redis_connection()
    message_key = f"message:{message_id}"
    
    # 检查用户是否存在
    if(check_message_exists(redis_client,message_id)==0):
        return False
    
    # 更新字段
    results = redis_client.hset(message_key, field_name, field_value)
    if(bool(results)==True):
        return 1
    else:
        return 0

def find_message_by_field(field_value, field_name='chat_id', limit=8):
    """
    根据字段值查找消息，返回最近的几条记录
    """
    redis_client = redisdb.get_redis_connection()
    records = []
    
    message_keys = redis_client.keys("message:*")
    
    for message_key in message_keys:
        # 获取字段值
        value = redis_client.hget(message_key, field_name)
        if value == field_value:
            record_id = int(message_key.split(':')[1])
            record_data = redis_client.hgetall(message_key)
            records.append((record_id, record_data))
    
    # 按记录ID降序排序（ID越大越新）
    records.sort(key=lambda x: x[0], reverse=True)
    
    # 返回最近的几条记录的数据部分
    return [record_data for record_id, record_data in records[:limit]]

def delete_message_by_chat_id(chat_id):
    redis_client = redisdb.get_redis_connection() 
    message_keys = redis_client.keys("message:*")
    
    for message_key in message_keys:
        # 获取字段值
        value = redis_client.hget(message_key, 'chat_id')
        if value == chat_id:
            delete_message(int(message_key.split(':')[1]))

def test():
    clear_all_message()
    result=find_message_by_field('1')
    print(result)
    result=find_message_by_field('2')
    print(result)
    print('添加消息功能测试')
    result=add_message('你好',0,1)
    print(result)
    result=add_message('您好',1,1)
    print(result)
    result=add_message('不好',0,2)
    print(result)
    result=find_message_by_field('1')
    print(result)
    result=find_message_by_field('2')
    print(result)
    print('删除对话功能测试')
    delete_message_by_chat_id('1')
    result=find_message_by_field('1')
    print(result)
    result=find_message_by_field('2')
    print(result)
    clear_all_message()

if __name__ == "__main__":
    test()