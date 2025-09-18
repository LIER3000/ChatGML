import socket
import json
import datetime

def send_array_to_server(array, server_host='127.0.0.1', server_port=12345):
    """
    向服务器发送数组并接收处理结果
    """
    # 创建一个 TCP/IP 套接字
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # 连接到服务器
        client_socket.connect((server_host, server_port))
        print(f"[已连接] 成功连接到服务器 {server_host}:{server_port}")
        
        # 将数组转换为JSON字符串
        array_json = json.dumps(array, ensure_ascii=False)
        print(f"[发送数据] 数组: {array}")
        
        # 发送JSON数据到服务器
        client_socket.send(array_json.encode('utf-8'))
        
        # 接收服务器的响应
        response_data = client_socket.recv(4096)
        
        # 解码响应数据
        response_str = response_data.decode('utf-8')
        
        # 尝试解析为JSON，如果不是JSON则直接打印
        try:
            response = json.loads(response_str)
            # 格式化输出结果
            return response
                
        except json.JSONDecodeError:
            # 如果不是JSON，直接打印错误信息
            return response_str
            
    except ConnectionRefusedError:
        print(f"[连接失败] 无法连接到服务器 {server_host}:{server_port}，请检查服务器是否运行。")
    except ConnectionResetError:
        print("[连接错误] 服务器连接被重置。")
    except Exception as e:
        print(f"[错误] {e}")
    finally:
        client_socket.close()
        print("\n连接已关闭。")

if __name__ == "__main__":
    array=['db','senworddb','get_all_senword']
    res=send_array_to_server(array)
    print(res)
    print(res[0][1])