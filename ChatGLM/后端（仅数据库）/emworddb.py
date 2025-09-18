import redisdb

def clear_all_emword():
    """
    清空所有记录数据
    """
    redis_client = redisdb.get_redis_connection()
    emword_keys = redis_client.keys("emword:*")
    if not emword_keys:
        return 0
    redis_client.delete("id:counter:emword")
    return redis_client.delete(*emword_keys)

def get_next_id_with_init(redis_client,counter_key="id:counter:emword", initial_id=1):
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

def check_emword_exists(redis_client,emword_id):
    """
    检查是否存在
    """
    emword_key = f"emword:{emword_id}"
    exists = redis_client.exists(emword_key)
    return bool(exists) 

def add_emword(emword_text,emword_sentiment,emword_sen_height):
    redis_client=redisdb.get_redis_connection()
    emword_id=get_next_id_with_init(redis_client)
    emword_data={
        'emword_id': emword_id,
        'emword_text': emword_text,
        'emword_sentiment': emword_sentiment,
        'emword_sen_height': emword_sen_height
    }
    pipe=redis_client.pipeline()
    pipe.hset(f"emword:{emword_id}", mapping=emword_data)
    results = pipe.execute()
    return emword_id
def delete_emword(emword_id):
    redis_client=redisdb.get_redis_connection()
    if(check_emword_exists(redis_client,emword_id)==0):
        return False
    emword_key = f"emword:{emword_id}"
    results = redis_client.delete(emword_key)
    return bool(results)

def get_all_senword():
    redis_client=redisdb.get_redis_connection()
    all_emword = []
    cursor = '0'
    pattern = "emword:*"
    
    try:
        # 使用SCAN命令迭代获取所有敏感词键
        while cursor != 0:
            cursor, keys = redis_client.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                with redis_client.pipeline() as pipe:
                    for key in keys:
                        pipe.hgetall(key)
                        result = pipe.execute()
                        all_emword.append(result)
        return all_emword
        
    except Exception as e:
        return []
    
def check_emword_by_field(field_value, field_name='emword_text'):
    """
    根据字段值查找，返回最近的几条记录（包含全部字段）
    """
    redis_client = redisdb.get_redis_connection()
    emwords = []
    
    emword_keys = redis_client.keys("chat:*")
    
    for emword_key in emword_keys:
        # 获取字段值
        value = redis_client.hget(emword_key, field_name)
        if value == field_value:
            record_id = int(emword_key.split(':')[1])
            # 获取所有字段
            record_data = redis_client.hgetall(emword_key)
            emwords.append((record_id, record_data))
    
    # 按记录ID降序排序（ID越大越新）
    emwords.sort(key=lambda x: x[0], reverse=True)
    
    # 返回最近的几条记录的完整数据
    return 1 if emwords else 0

def update_emword_field(emword_id, field_name, field_value):
    """
    更新特定字段
    """

    redis_client = redisdb.get_redis_connection()
    emword_key = f"emword:{emword_id}"
    
    # 检查用户是否存在
    if(check_emword_exists(redis_client,emword_id)==0):
        return 0
    
    # 更新字段
    results = redis_client.hset(emword_key, field_name, field_value)
    if(bool(results)==True):
        return 1
    else:
        return 0
    
def test():
    clear_all_emword()
    result=get_all_senword()
    print(result)
    print('添加情感词功能测试')
    add_emword('开心','happy','1')
    add_emword('哭','sad','2')
    result=get_all_senword()
    print(result)
    print('删除情感词功能测试')
    delete_emword(1)
    result=get_all_senword()
    print(result)
    clear_all_emword()
    add_emword('开心','高兴','1')

if __name__ == "__main__":
    test()