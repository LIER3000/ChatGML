import redisdb

def clear_all_senword():
    """
    清空所有记录数据
    """
    redis_client = redisdb.get_redis_connection()
    senword_keys = redis_client.keys("senword:*")
    if not senword_keys:
        return 0
    redis_client.delete("id:counter:senword")
    return redis_client.delete(*senword_keys)

def get_next_id_with_init(redis_client,counter_key="id:counter:senword", initial_id=1):
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

def check_senword_exists(redis_client,senword_id):
    """
    检查是否存在
    """
    senword_key = f"senword:{senword_id}"
    exists = redis_client.exists(senword_key)
    return bool(exists) 

def add_senword(text):
    redis_client=redisdb.get_redis_connection()
    senword_id=get_next_id_with_init(redis_client)
    senword_data={
        'senword_id': senword_id,
        'senword_text': text
    }
    pipe=redis_client.pipeline()
    pipe.hset(f"senword:{senword_id}", mapping=senword_data)
    results = pipe.execute()
    return senword_id

def delete_senword(senword_id):
    redis_client=redisdb.get_redis_connection()
    if(check_senword_exists(redis_client,senword_id)==0):
        return False
    senword_key = f"senword:{senword_id}"
    results = redis_client.delete(senword_key)
    return bool(results)

def get_senword_by_id(senword_id):
    redis_client=redisdb.get_redis_connection()
    senword_key = f"senword:{senword_id}"
    return redis_client.hmget(senword_key, 'senword_text')

def get_all_senword():
    redis_client=redisdb.get_redis_connection()
    all_senword_texts = []
    cursor = '0'
    pattern = "senword:*"
    
    try:
        # 使用SCAN命令迭代获取所有敏感词键
        while cursor != 0:
            cursor, keys = redis_client.scan(cursor=cursor, match=pattern, count=100)
            # 批量获取所有键的senword_text字段
            if keys:
                # 使用pipeline批量操作提高效率
                with redis_client.pipeline() as pipe:
                    for key in keys:
                        pipe.hget(key, 'senword_text')
                        result = pipe.execute()
                        all_senword_texts.append((int(key.split(':')[1]),result))
        return all_senword_texts
        
    except Exception as e:
        return []
    
def test():
    clear_all_senword()
    result=get_all_senword()
    print(result)
    print('添加敏感词功能测试')
    add_senword('草')
    add_senword('我去')
    add_senword('滚')
    result=get_all_senword()
    print(result)
    print('删除敏感词功能测试')
    delete_senword('2')
    result=get_all_senword()
    print(result)
    clear_all_senword()
    add_senword('草')

if __name__ == "__main__":
    test()