from datetime import datetime, timedelta
import json
import time
import redisdb
import bcrypt
    
def clear_all_users():
    """
    清空所有用户数据
    """
    redis_client = redisdb.get_redis_connection()
    user_keys = redis_client.keys("user:*")
    if not user_keys:
        return 0
    return redis_client.delete(*user_keys)
    
def check_user_exists(user_id):
    """
    检查用户ID是否存在
    """
    redis_client=redisdb.get_redis_connection()
    user_key = f"user:{user_id}"
    exists = redis_client.exists(user_key)
    if(bool(exists)==True):
        return 1
    else:
        return 0 

def hash_password(password: str) -> bytes:
    """加密密码"""
    # 生成盐并哈希密码
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed
    
def add_user(user_id,user_name,user_password):
    redis_client = redisdb.get_redis_connection()
    timestamp = datetime.now()
    user_data={
        'user_id': user_id,
        'user_name': user_name,
        'user_password': user_password,
        'user_time': timestamp.isoformat(),
        'user_interest': json.dumps(["通用兴趣"]),
        'user_strong_interest': json.dumps(["强兴趣"]),
        'user_identity': 0
    }
    if(check_user_exists(user_id)):
        return False
    pipe=redis_client.pipeline()
    pipe.hset(f"user:{user_id}", mapping=user_data)
    results = pipe.execute()
    if(bool(results)==True):
        return 1
    else:
        return 0 

def add_user_manager():
    redis_client = redisdb.get_redis_connection()
    timestamp = datetime.now()
    user_data={
        'user_id': 123456,
        'user_name': 123456,
        'user_password': hash_password('12345678'),
        'user_time': timestamp.isoformat(),
        'user_interest': json.dumps(["通用兴趣"]),
        'user_strong_interest': json.dumps(["强兴趣"]),
        'user_identity': 1
    }
    if(check_user_exists(123456)):
        return 0
    pipe=redis_client.pipeline()
    pipe.hset(f"user:{123456}", mapping=user_data)
    results = pipe.execute()
    if(bool(results)==True):
        return 1
    else:
        return 0 

def delete_user_by_id(user_id):
    redis_client=redisdb.get_redis_connection()
    if(check_user_exists(user_id)==0):
        return 0
    user_key = f"user:{user_id}"
    results = redis_client.delete(user_key)
    if(bool(results)==True):
        return 1
    else:
        return 0 

def get_user_fields(user_id, fields):
    """
    获取用户特定字段的信息
    """
    redis_client=redisdb.get_redis_connection()
    user_key = f"user:{user_id}"
    if(check_user_exists(user_id)==0):
        return 0
    if (fields=='all'):
        # 获取所有字段
        return redis_client.hgetall(user_key)
    else:
        # 获取指定字段
        if isinstance(fields, str):
            fields = [fields]
        return redis_client.hmget(user_key, fields)
    
def update_user_field(user_id, field_name, field_value):
    """
    更新用户特定字段
    """

    redis_client = redisdb.get_redis_connection()
    user_key = f"user:{user_id}"
    
    # 检查用户是否存在
    if(check_user_exists(user_id)==0):
        return 0
    
    # 更新字段
    results = redis_client.hset(user_key, field_name, field_value)
    if(bool(results)==True):
        return 1
    else:
        return 0 
    
def get_all_users():
    """
    获取所有用户信息（使用 SCAN 安全迭代）
    """
    redis_client = redisdb.get_redis_connection()
    users = []
    cursor = 0
    pattern = "user:*"
    
    try:
        while True:
            cursor, keys = redis_client.scan(cursor=cursor, match=pattern, count=100)
            
            # 批量获取所有用户数据
            if keys:
                pipe = redis_client.pipeline()
                for key in keys:
                    pipe.hgetall(key)
                user_data_list = pipe.execute()
                
                # 处理用户数据
                for key, user_data in zip(keys, user_data_list):
                    if user_data:
                        users.append(user_data)
            
            # 迭代完成
            if cursor == 0:
                break
                
    except Exception as e:
        print(f"获取用户列表时出错: {e}")
    
    return users

def test():
    clear_all_users()
    print("添加用户功能测试")
    add_user_manager()
    result=add_user(123,'123','123456')
    print(result)
    result=add_user(111,'123','123456')
    print(result)
    result=get_all_users()
    print(result)
    print("搜索用户信息功能测试")
    result=get_user_fields(123,'user_name')
    print(result)
    result=get_user_fields(123,'user_password')
    print(result)
    result=get_user_fields(123456,'user_password')
    print(result)
    result=get_user_fields(123,'user_time')
    print(result)
    result=get_user_fields(123,'all')
    print(result)
    print("更新用户信息测试")
    result=get_user_fields(123,'user_name')
    print(result)
    update_user_field(123,'user_name',456)
    result=get_user_fields(123,'user_name')
    print(result)
    print("删除用户功能测试")
    result=delete_user_by_id(123)
    print(result)
    result=delete_user_by_id(123)
    print(result)
    clear_all_users()
    add_user_manager()

if __name__ == "__main__":
    test()
    add_user_manager()