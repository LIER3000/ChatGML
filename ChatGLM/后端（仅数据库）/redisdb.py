import redis

def get_redis_connection():
    try:
        r = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True,
            socket_connect_timeout=3
        )
        r.ping()
        return r
    except redis.ConnectionError:
        print("❌ 无法连接到 Redis 服务器")
        print("请确保 Redis 服务器正在运行")
        return None