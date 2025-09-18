import socket
import threading
import json
import db_dispatch


def handle_client(conn, addr):
    """
    处理一个单独的客户端连接，接收数组并处理
    """
    print(f"[新连接] {addr} 已连接。")
    
    # 设置连接为阻塞模式
    conn.setblocking(True)
    
    # 循环接收该客户端发来的消息
    while True:
        try:
            # 接收数据 (最多接收 4096 字节)
            data = conn.recv(4096)
            
            # 如果接收到空数据，表示客户端主动关闭了连接
            if not data:
                print(f"[连接关闭] {addr} 断开了连接。")
                break
                
            # 将接收到的字节数据解码为字符串，然后解析为JSON（数组）
            try:
                received_array = json.loads(data.decode('utf-8'))
                print(f"[来自 {addr}] 接收到数组：{received_array}")
                
                # 验证接收到的是否是数组
                if not isinstance(received_array, list):
                    error_msg = "错误：请发送一个有效的数组"
                    conn.send(error_msg.encode('utf-8'))
                    continue
                
                # 处理数据：对数组进行各种计算
                if(received_array[0]=='db'):
                    del(received_array[0])
                    response_data=db_dispatch.dispatch(received_array)
                    print(response_data)
                else:
                    response_data = {
                    "original_array": received_array,
                    }
                
                
                # 将响应结果转换为JSON字符串，然后编码为字节数据发送回客户端
                response_json = json.dumps(response_data, ensure_ascii=False)
                conn.send(response_json.encode('utf-8'))
                
            except json.JSONDecodeError:
                error_msg = "错误：无法解析JSON数据，请发送有效的JSON数组"
                print(f"[错误] {addr} 发送了无效的JSON数据")
                conn.send(error_msg.encode('utf-8'))
                
        except ConnectionResetError:
            print(f"[连接异常] {addr} 连接被重置。")
            break
        except Exception as e:
            print(f"[处理 {addr} 时发生错误]： {e}")
            break
            
    # 关闭这个客户端的连接套接字
    conn.close()

def start_server(host='127.0.0.1', port=12345):
    """
    启动服务器
    """
    # 创建一个 TCP/IP 套接字
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 设置 SO_REUSEADDR 选项
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        # 将套接字绑定到指定的主机和端口
        server_socket.bind((host, port))
        # 开始监听
        server_socket.listen(5)
        print(f"[服务器启动] 监听于 {host}:{port} ...")
        print("[服务器就绪] 等待接收客户端发送的数组...")
        
        # 循环接受新的客户端连接
        while True:
            # 等待并接受一个客户端连接
            conn, addr = server_socket.accept()
            
            # 为每个新的客户端创建一个新的线程来处理
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.daemon = True
            client_thread.start()
            print(f"[活跃连接] {threading.active_count() - 1}")
            
    except KeyboardInterrupt:
        print("\n[服务器关闭] 由用户中断。")
    except Exception as e:
        print(f"[服务器错误] {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()