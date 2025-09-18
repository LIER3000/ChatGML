from datetime import datetime, timedelta
import json
import time
import redisdb
    
def clear_all_admin_record():
    """
    清空所有记录数据
    """
    redis_client = redisdb.get_redis_connection()
    admin_record_keys = redis_client.keys("admin_record:*")
    if not admin_record_keys:
        return 0
    redis_client.delete("id:counter:admin_record")
    return redis_client.delete(*admin_record_keys)

def get_next_id_with_init(redis_client,counter_key="id:counter:admin_record", initial_id=1):
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

def check_admin_record_exists(redis_client,admin_record_id):
    """
    检查记录ID是否存在
    """
    admin_record_key = f"admin_record:{admin_record_id}"
    exists = redis_client.exists(admin_record_key)
    return bool(exists) 
    
def add_admin_record(admin_type,operator_id,target_user_id):
    redis_client = redisdb.get_redis_connection()
    admin_id = get_next_id_with_init(redis_client)
    admin_time=datetime.now()
    admin_record_data ={
        'admin_id': admin_id,
        'admin_type': admin_type,
        'admin_time': admin_time.isoformat(),
        'operator_id': operator_id,
        'target_user_id': target_user_id
    }
    pipe=redis_client.pipeline()
    pipe.hset(f"admin_record:{admin_id}", mapping=admin_record_data)
    results = pipe.execute()
    return bool(results)

def delete_admin_record_by_id(admin_id):
    redis_client = redisdb.get_redis_connection()
    if(check_admin_record_exists(redis_client,admin_id)==0):
        return False
    admin_key=f"admin_record:{admin_id}"
    results=redis_client.delete(admin_key)
    return bool(results)

def find_admin_record_by_field(field_name, field_value, limit=8):
    """
    根据字段值查找管理员记录，返回最近的几条记录
    """
    redis_client = redisdb.get_redis_connection()
    records = []
    
    # 获取所有管理员记录键
    admin_keys = redis_client.keys("admin_record:*")
    
    for admin_key in admin_keys:
        # 获取字段值
        value = redis_client.hget(admin_key, field_name)
        if value == field_value:
            record_id = int(admin_key.split(':')[1])
            record_data = redis_client.hgetall(admin_key)
            records.append((record_id, record_data))
    
    # 按记录ID降序排序（ID越大越新）
    records.sort(key=lambda x: x[0], reverse=True)
    
    # 返回最近的几条记录的数据部分
    return [record_data for record_id, record_data in records[:limit]]

def test():
    clear_all_admin_record()
    print('管理员123')
    result=find_admin_record_by_field('operator_id','123')
    print(result)
    print('管理员111')
    result=find_admin_record_by_field('operator_id','111')
    print(result)
    print('添加记录功能测试')
    add_admin_record('授权',123,111)
    add_admin_record('授权',111,111) 
    add_admin_record('禁用',123,333)
    print('管理员123')
    result=find_admin_record_by_field('operator_id','123')
    print(result)
    print('管理员111')
    result=find_admin_record_by_field('operator_id','111')
    print(result)
    print('删除功能测试')
    delete_admin_record_by_id(1)
    print('管理员123')
    result=find_admin_record_by_field('operator_id','123')
    print(result)
    print('管理员111')
    result=find_admin_record_by_field('operator_id','111')
    print(result)
    clear_all_admin_record()

if __name__ == "__main__":
    test()